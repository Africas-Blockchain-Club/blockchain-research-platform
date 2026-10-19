"""
Refresh the live snapshot of every featured blockchain, keep a current
data-only report for each, then rebuild the site.

Runs in the background on the production machine (scripts/start.sh), so the
blockchain pages show current network data without anyone generating a
report. It reads only free public endpoints, makes no AI call and never
touches a saved report.

  python scripts/refresh_networks.py           refresh once and rebuild
  python scripts/refresh_networks.py --loop    refresh every REFRESH_MINUTES (default 15)
"""
import argparse
import datetime
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from config import NETWORK_DIR  # noqa: E402
from data_analytics.chains import FEATURED, PROFILES  # noqa: E402
from data_analytics.risk_profile import CHECKS_VERSION  # noqa: E402
from data_engineering.derivatives import fetch_open_interest  # noqa: E402
from data_engineering.networks import fetch_network  # noqa: E402

log = logging.getLogger("refresh")


def fetch_prices():
    """Price and 24-hour change for every featured chain's asset, in one call."""
    ids = ",".join(PROFILES[s]["coingecko_id"] for s in FEATURED)
    headers = {}
    if os.getenv("COINGECKO_API_KEY"):
        headers["x-cg-demo-api-key"] = os.getenv("COINGECKO_API_KEY")
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ids, "vs_currencies": "usd,zar", "include_24hr_change": "true", "include_market_cap": "true"},
            headers=headers, timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.warning("Price refresh failed: %s", e)
        return {}


def _write_json(path, data):
    # Write then rename, so the site never reads a half-written file
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def refresh_once():
    NETWORK_DIR.mkdir(parents=True, exist_ok=True)
    prices = fetch_prices()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Every source each featured chain needs, checked from where the site runs:
    # some exchanges refuse requests from some locations, so only this machine's
    # view counts. Names only; error text stays in the log.
    problems = {} if prices else {"ALL": ["CoinGecko prices"]}
    for symbol in FEATURED:
        snapshot = {
            "symbol": symbol,
            "fetched_at": now,
            "network": fetch_network(symbol),
            "price": prices.get(PROFILES[symbol]["coingecko_id"]),
        }
        _write_json(NETWORK_DIR / f"{symbol}.json", snapshot)
        status = snapshot["network"].get("error") or "ok"
        log.info("%s network snapshot: %s", symbol, status)
        failed = ["network"] if snapshot["network"].get("error") else []
        if not snapshot["price"]:
            failed.append("price")
        futures = fetch_open_interest(symbol)
        failed += [f"{venue} futures" for venue in futures["failed"]]
        if failed:
            log.warning("%s sources not answering: %s %s", symbol, failed, futures["failed"])
            problems[symbol] = failed

    for symbol, failed in refresh_featured_reports().items():
        problems.setdefault(symbol, []).extend(f"report: {name}" for name in failed)
    _write_json(NETWORK_DIR / "sources.json", {"checked_at": now, "chains": list(FEATURED), "problems": problems})

    from sitegen.build import build_site

    build_site()


def refresh_featured_reports():
    """Keep a current data-only report for every featured chain. A report is
    regenerated once it is older than REPORT_REFRESH_HOURS (default 24), or
    sooner if a source failed when it was made (a rate limit, an outage). A paid
    AI write-up is never overwritten. Reports are spaced out so the free
    CoinGecko tier does not rate-limit them."""
    from tools import report_store
    from tools.report_generator import fetch_and_analyse, save_data_report

    with report_store.site_rebuilds_suspended():
        return _refresh_reports(report_store, fetch_and_analyse, save_data_report)


def _refresh_reports(report_store, fetch_and_analyse, save_data_report):
    """Returns {symbol: [source names]} for reports made with a source failing."""
    # The caller rebuilds the site once afterwards, not once per report
    failures = {}
    max_age = datetime.timedelta(hours=int(os.getenv("REPORT_REFRESH_HOURS") or "24"))
    now = datetime.datetime.now(datetime.timezone.utc)
    for symbol in FEATURED:
        loaded = report_store.load_report(symbol)
        if loaded:
            meta = loaded[0]
            if meta.get("mode") == "ai":
                continue
            generated = datetime.datetime.fromisoformat(meta["generated_at"])
            # A recent, complete report on the current checks is left alone; anything else is redone
            current = meta.get("checks_version") == CHECKS_VERSION
            if now - generated < max_age and not meta.get("source_errors") and current:
                continue
        try:
            analysis = fetch_and_analyse(symbol, log_fn=lambda _msg: None)
            meta = save_data_report(analysis)
            if meta.get("source_errors"):
                failures[symbol] = sorted(meta["source_errors"])
            log.info("%s report refreshed: %s flagged, %s clear, %s no data",
                     symbol, meta["flagged"], meta["clear"], meta["no_data"])
        except Exception:
            log.exception("%s report refresh failed", symbol)
            failures[symbol] = ["report refresh"]
        time.sleep(int(os.getenv("REPORT_REFRESH_SPACING_SECONDS") or "20"))
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--loop", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    minutes = int(os.getenv("REFRESH_MINUTES") or "15")
    while True:
        try:
            refresh_once()
        except Exception:
            # A failed refresh must never stop the next one; the site keeps its last good pages
            log.exception("Refresh failed")
        if not args.loop:
            return
        time.sleep(minutes * 60)


if __name__ == "__main__":
    main()
