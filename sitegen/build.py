"""
The static public site: plain HTML pages generated from the blockchain
profiles, the live network snapshots and the saved reports.

Visitors read these pages straight from Caddy, so they load like any normal
website; only live research and payments open the Streamlit app. The site is
rebuilt at start-up, after every saved report, and after each background
network refresh (scripts/refresh_networks.py).

Security: report text can be written by an AI model, so it is treated as
untrusted. Raw HTML in markdown is escaped, links are limited to http(s),
mailto and in-page targets, and Jinja2 autoescapes every value. The content
security policy in the Caddyfile is the second line of defence.

  python -m sitegen.build            build into SITE_DIR
  python -m sitegen.build --out DIR  build somewhere else (local preview)
"""
import argparse
import datetime
import json
import logging
import os
import re
import shutil
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from config import BUILD, DATA_DIR, NETWORK_DIR, ROOT_DIR, SETTINGS, SITE_DIR
from data_analytics.chains import CHECKED, FEATURED, PROFILES
from data_analytics.risk_profile import NOT_COVERED, STATUS_LABELS, compute_risk_checks, summarise_checks
from data_science.compliance import SHORT_DISCLAIMER, long_disclaimer
from tools import report_store

log = logging.getLogger(__name__)

HERE = Path(__file__).resolve().parent
MEDIA = ["abc-logo-tile.png", "abc-logo-tile-180.png", "abc-mascot.png", "abc-home-still.jpg", "01_home_loop.mp4"]
PDF_CACHE = DATA_DIR / "pdf-cache"

_SAFE_HREF = re.compile(r'href="(?!https?://|mailto:|#|/)[^"]*"', re.IGNORECASE)


def safe_markdown(text):
    """Markdown to HTML with raw HTML neutralised and only safe link targets."""
    html = markdown.markdown(text.replace("<", "&lt;"), extensions=["tables", "sane_lists"])
    html = _SAFE_HREF.sub('href="#"', html)
    # Long reports scroll tables inside themselves on phones
    html = html.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")
    # Safe to mark as markup: raw HTML was escaped and unsafe links removed above, which
    # tests/test_sitegen.py proves with a planted <script> and a javascript: link
    return Markup(html)  # nosec B704


def _snapshot(symbol):
    path = NETWORK_DIR / f"{symbol}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _when(iso):
    try:
        return datetime.datetime.fromisoformat(iso).strftime("%d %b %Y, %H:%M UTC")
    except (TypeError, ValueError):
        return "unknown time"


def _report_pdf(token, markdown_text, md_path):
    """PDF for a report, cached by the markdown file's modification time."""
    from tools.pdf_export import markdown_to_pdf

    PDF_CACHE.mkdir(parents=True, exist_ok=True)
    stamp = int(md_path.stat().st_mtime) if md_path.exists() else 0
    cached = PDF_CACHE / f"{token}-{stamp}.pdf"
    if not cached.exists():
        pdf, error = markdown_to_pdf(markdown_text)
        if error:
            log.warning("PDF for %s failed: %s", token, error)
            return None
        for old in PDF_CACHE.glob(f"{token}-*.pdf"):
            old.unlink(missing_ok=True)
        cached.write_bytes(pdf)
    return cached


def _environment():
    env = Environment(loader=FileSystemLoader(HERE / "templates"), autoescape=select_autoescape(["html"]))
    env.globals.update(
        build=BUILD, settings=SETTINGS, app_url=SETTINGS.app_url, disclaimer=SHORT_DISCLAIMER,
        status_labels=STATUS_LABELS, year=datetime.date.today().year,
    )
    env.filters["when"] = _when
    return env


def _chain_cards(reports_by_token):
    cards = []
    for symbol in FEATURED:
        profile = PROFILES[symbol]
        snapshot = _snapshot(symbol) or {}
        cards.append({
            "symbol": symbol,
            "profile": profile,
            "price": snapshot.get("price") or {},
            "network": snapshot.get("network") or {},
            "fetched_at": snapshot.get("fetched_at"),
            "report": reports_by_token.get(symbol),
        })
    return cards


def build_site(out_dir=None):
    """Render every page into out_dir (default SITE_DIR), swapping it in whole."""
    out_dir = Path(out_dir or SITE_DIR)
    # Each build gets its own folder; out_dir is a symlink switched to it in one
    # atomic step, so a visitor never lands in the gap between two versions
    builds = out_dir.with_name(f".{out_dir.name}-builds")
    staging = builds / f"{datetime.datetime.now():%Y%m%d%H%M%S%f}-{os.getpid()}"
    (staging / "static").mkdir(parents=True)
    (staging / "blockchains").mkdir()
    (staging / "reports").mkdir()
    # Which data sources answered on the server's last refresh, for the monitor. It holds
    # source names only, never error text, which can contain an endpoint's URL or key.
    (staging / "status").mkdir()
    for name in ("sources.json", "prices.json"):
        if (NETWORK_DIR / name).exists():
            shutil.copy2(NETWORK_DIR / name, staging / "status" / name)

    for name in ("abc-shell.css", "wtc-shell.js", "site.css", "site.js", "theme.js"):
        shutil.copy2(HERE / "static" / name, staging / "static" / name)
    for name in MEDIA:
        source = ROOT_DIR / "dashboards" / "static" / name
        if source.exists():
            shutil.copy2(source, staging / "static" / name)

    env = _environment()
    reports = report_store.list_reports()
    by_token = {meta["token"]: meta for meta in reports}
    cards = _chain_cards(by_token)

    def write(path, template, **context):
        (staging / path).write_text(env.get_template(template).render(**context), encoding="utf-8")

    write("index.html", "index.html", home=True, cards=cards, reports=reports[:6], page="home")
    write("blockchains/index.html", "chains.html", cards=cards, page="blockchains", checked=CHECKED)
    for card in cards:
        write(f"blockchains/{card['profile']['slug']}.html", "chain.html", card=card, page="blockchains",
              checked=CHECKED)

    for meta in reports:
        token = meta["token"]
        loaded = report_store.load_report(token)
        if not loaded:
            continue
        meta, text = loaded
        sections = [(title, safe_markdown(body)) for title, body in report_store.split_sections(text)
                    if title not in ("Introduction", "Risk Checks")]
        md_path = report_store.REPORTS_DIR / f"{token}_research_report.md"
        (staging / "reports" / f"{token}.md").write_text(text, encoding="utf-8")
        pdf = _report_pdf(token, text, md_path)
        if pdf:
            shutil.copy2(pdf, staging / "reports" / f"{token}.pdf")
        write(f"reports/{token}.html", "report.html", meta=meta, sections=sections, page="reports",
              counts=summarise_checks(meta["risk_checks"]), has_pdf=bool(pdf),
              profile=PROFILES.get(token), long_disclaimer=safe_markdown(long_disclaimer()),
              not_covered=NOT_COVERED, ai_on_offer=meta["mode"] != "ai" and SETTINGS.ai_enabled)
    write("reports/index.html", "reports.html", reports=reports, page="reports")
    # The method page lists the checks as a chain's report runs them: with exchange depth
    method_checks = compute_risk_checks({"market_depth": {"depth_down_2pct_usd": 0}})
    write("how-it-works.html", "method.html", page="method", checks=method_checks, not_covered=NOT_COVERED,
          featured=[PROFILES[s] for s in FEATURED])
    write("404.html", "404.html", page="")

    _publish(staging, out_dir)
    log.info("Site built: %d blockchains, %d reports, into %s", len(cards), len(reports), out_dir)
    return out_dir


def _publish(build_dir, out_dir):
    """Point out_dir at build_dir atomically, then remove stale builds."""
    if out_dir.exists() and not out_dir.is_symlink():
        # A real folder from before builds were versioned: move it aside once
        shutil.rmtree(out_dir.with_name(out_dir.name + ".legacy"), ignore_errors=True)
        out_dir.rename(out_dir.with_name(out_dir.name + ".legacy"))
    link = out_dir.with_name(f".{out_dir.name}.link-{os.getpid()}")
    link.unlink(missing_ok=True)
    link.symlink_to(build_dir, target_is_directory=True)
    os.replace(link, out_dir)  # atomic on POSIX
    shutil.rmtree(out_dir.with_name(out_dir.name + ".legacy"), ignore_errors=True)
    # Keep the live build and any build started in the last ten minutes (it may
    # belong to a concurrent rebuild that has not switched yet)
    cutoff = datetime.datetime.now().timestamp() - 600
    for old in build_dir.parent.iterdir():
        if old != build_dir and old.stat().st_mtime < cutoff:
            shutil.rmtree(old, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Build the static public site.")
    parser.add_argument("--out", default=None, help=f"output folder (default {SITE_DIR})")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    print(build_site(args.out))


if __name__ == "__main__":
    main()
