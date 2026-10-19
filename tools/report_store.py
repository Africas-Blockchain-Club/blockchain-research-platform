"""
Reading and writing reports: the one place that knows the file layout.

Each report is two files in reports/:
  {TOKEN}_research_report.md    the human-readable report
  {TOKEN}_research_report.json  metadata and the risk checks, for the dashboard

The markdown always opens with the disclaimer and always closes with the risk
checks and the sources section. Those three parts are written by code, never
by a model, so they cannot be dropped or reworded by one.
"""
import contextlib
import datetime
import json
import logging
import re

import db
from config import REPORTS_DIR, SETTINGS
from data_analytics.risk_profile import CHECKS_VERSION, risk_checks_markdown, summarise_checks
from data_science.compliance import long_disclaimer

log = logging.getLogger(__name__)

FORMAT_VERSION = 3
MODE_AI = "ai"
MODE_DATA = "data"

_SOURCES = [
    ("DexScreener", "Main exchange pool: price, liquidity, volume, pool balances"),
    ("CoinGecko", "Market cap, supply, price history, project description, exchange rate"),
    ("CoinMarketCap", "Whether the token is listed (listing check only)"),
    ("Google News RSS", "Recent headlines"),
    ("DefiLlama", "Total value locked and protocol category"),
    ("CoinGecko exchange tickers", "Order-book depth on large exchanges"),
    ("OKX, Bitget, Gate, Hyperliquid", "Open interest on perpetual futures (public APIs)"),
    ("Coinglass", "Open interest and liquidations, when an API key is set"),
    ("Ultrasound.money", "ETH burn data (ETH only)"),
]


_TOKEN_PATTERN = re.compile(r"^[A-Z0-9]{1,20}$")


def is_valid_token(token):
    """Tickers are letters and digits only. Checked before any token is used
    in a file path, so a crafted link cannot read files outside reports/."""
    return bool(_TOKEN_PATTERN.match(str(token or "").upper()))


def _paths(token):
    if not is_valid_token(token):
        raise ValueError(f"{token!r} is not a valid token symbol.")
    stem = REPORTS_DIR / f"{token.upper()}_research_report"
    return stem.with_suffix(".md"), stem.with_suffix(".json")


def _sources_markdown(mode, model, generated_at):
    lines = [
        "## Sources and Limitations",
        "",
        "| Source | What It Provides |",
        "|---|---|",
        *[f"| {name} | {what} |" for name, what in _SOURCES],
        "",
        f"- The data is a snapshot taken on {generated_at:%d %B %Y at %H:%M} UTC. Markets move; check the sources for current values.",
        "- The risk-check thresholds are teaching thresholds chosen by this platform, not industry standards.",
    ]
    if mode == MODE_AI:
        lines.append(
            f"- The explanations were written by an AI model ({model}). AI can make mistakes: check every "
            "figure against the sources above before you rely on it."
        )
    else:
        lines.append("- This is the data-only report. No AI wrote any part of it.")
    lines.append("")
    return "\n".join(lines)


def _insert_disclaimer(body):
    """Put the disclaimer straight after the report title."""
    lines = body.strip().splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join([lines[0], "", long_disclaimer(), "", *lines[1:]])
    return "\n".join([long_disclaimer(), "", *lines])


def compose_markdown(body, *, mode, model, risk_checks, generated_at):
    return "\n".join(
        [
            _insert_disclaimer(body),
            "",
            risk_checks_markdown(risk_checks),
            _sources_markdown(mode, model, generated_at),
        ]
    )


def save_report(token, body, *, mode, model, risk_checks, data_summary, screenshot_path=None,
                payment_id=None, cost_usd=None, generated_at=None):
    """Write both files and the database row. Returns the metadata dict."""
    token = token.upper()
    generated_at = generated_at or datetime.datetime.now(datetime.timezone.utc)
    counts = summarise_checks(risk_checks)
    info = data_summary.get("token_info") or {}
    meta = {
        "format": FORMAT_VERSION,
        "token": token,
        "name": info.get("name") or token,
        "mode": mode,
        "model": model,
        "generated_at": generated_at.isoformat(),
        "flagged": counts["flagged"],
        "clear": counts["clear"],
        "no_data": counts["no_data"],
        "risk_checks": risk_checks,
        "checks_version": CHECKS_VERSION,
        "screenshot": screenshot_path,
        "price_usd": info.get("current_price_usd"),
        "market_cap_usd": info.get("market_cap_usd"),
        "fx": data_summary.get("fx"),
        # Sources that failed for this report, so an incomplete report can be redone
        "source_errors": data_summary.get("source_errors") or {},
        "cost_usd": cost_usd,
    }
    markdown = compose_markdown(body, mode=mode, model=model, risk_checks=risk_checks, generated_at=generated_at)
    frontmatter = (
        f"---\nToken: {token}\nMode: {mode}\nModel: {model or 'none'}\n"
        f"Generated: {meta['generated_at']}\nFormat: {FORMAT_VERSION}\n---\n\n"
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    md_path, json_path = _paths(token)
    md_path.write_text(frontmatter + markdown, encoding="utf-8")
    json_path.write_text(json.dumps(meta, indent=2, default=str) + "\n", encoding="utf-8")

    db.save_report(
        token_symbol=token,
        payment_id=payment_id,
        model=model or "none",
        screenshot_path=screenshot_path,
        markdown=frontmatter + markdown,
    )
    _rebuild_site()
    return meta


_rebuilds_suspended = False


@contextlib.contextmanager
def site_rebuilds_suspended():
    """Save several reports, then rebuild the site once (the caller does it)."""
    global _rebuilds_suspended
    previous, _rebuilds_suspended = _rebuilds_suspended, True
    try:
        yield
    finally:
        _rebuilds_suspended = previous


def _rebuild_site():
    """Publish the new report on the static site. A failed rebuild is logged
    loudly but never loses the saved report; the next rebuild picks it up."""
    if not SETTINGS.site_build_on_save or _rebuilds_suspended:
        return
    try:
        from sitegen.build import build_site

        build_site()
    except Exception:
        log.exception("The report was saved, but the static site could not be rebuilt")


def strip_frontmatter(text):
    match = re.match(r"^---\n.*?\n---\n+", text, re.DOTALL)
    return text[match.end():] if match else text


def list_reports(limit=None):
    """Metadata for every current-format report, newest first."""
    if not REPORTS_DIR.exists():
        return []
    reports = []
    for path in REPORTS_DIR.glob("*_research_report.json"):
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if meta.get("format") == FORMAT_VERSION:
            reports.append(meta)
    reports.sort(key=lambda m: m.get("generated_at", ""), reverse=True)
    return reports[:limit] if limit else reports


def load_report(token):
    """Return (meta, markdown) for a token, or None when there is no report."""
    md_path, json_path = _paths(token)
    if not md_path.exists() or not json_path.exists():
        return None
    meta = json.loads(json_path.read_text(encoding="utf-8"))
    return meta, strip_frontmatter(md_path.read_text(encoding="utf-8"))


def split_sections(markdown):
    """Split a report on its ## headings. Returns [(title, text), ...]; text
    before the first ## heading is returned under the title "Introduction"."""
    sections, title, lines = [], "Introduction", []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if any(part.strip() for part in lines):
                sections.append((title, "\n".join(lines)))
            title, lines = line[3:].strip(), [line]
        else:
            lines.append(line)
    if any(part.strip() for part in lines):
        sections.append((title, "\n".join(lines)))
    return sections
