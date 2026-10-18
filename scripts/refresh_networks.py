"""
Refresh the live snapshot of every featured blockchain, then rebuild the site.

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


def refresh_once():
    NETWORK_DIR.mkdir(parents=True, exist_ok=True)
    prices = fetch_prices()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for symbol in FEATURED:
        snapshot = {
            "symbol": symbol,
            "fetched_at": now,
            "network": fetch_network(symbol),
            "price": prices.get(PROFILES[symbol]["coingecko_id"]),
        }
        # Write then rename, so the site never reads a half-written file
        path = NETWORK_DIR / f"{symbol}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        tmp.replace(path)
        status = snapshot["network"].get("error") or "ok"
        log.info("%s network snapshot: %s", symbol, status)

    from sitegen.build import build_site

    build_site()


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
