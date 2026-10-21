"""
Keep the featured blockchains' prices current while people are on the site.

The site's pages are rebuilt every REFRESH_MINUTES (15), which is too slow for
a price. This loop asks CoinGecko for all seven prices in one request every
LIVE_PRICE_SECONDS (default 60) and writes them to /status/prices.json; the
pages read that file once a minute while they are open (sitegen/static/site.js).
One request a minute however many visitors there are, so the free CoinGecko
tier is never strained. LIVE_PRICE_SECONDS=0 switches it off, and the pages
keep the prices from their last build.

  python scripts/refresh_prices.py           write the prices once
  python scripts/refresh_prices.py --loop    keep them current
"""
import argparse
import datetime
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import NETWORK_DIR, SETTINGS, SITE_DIR  # noqa: E402
from data_analytics.chains import FEATURED, PROFILES  # noqa: E402
from scripts.refresh_networks import _write_json, fetch_prices  # noqa: E402

log = logging.getLogger("prices")


def price_file(raw, now=None):
    """The published file: {"fetched_at", "prices": {SYMBOL: {usd, zar, usd_24h_change}}}.
    A coin CoinGecko did not return is left out, so a page keeps its built price."""
    prices = {}
    for symbol in FEATURED:
        coin = raw.get(PROFILES[symbol]["coingecko_id"]) or {}
        if coin.get("usd"):
            prices[symbol] = {"usd": coin["usd"], "zar": coin.get("zar"), "usd_24h_change": coin.get("usd_24h_change")}
    fetched_at = (now or datetime.datetime.now(datetime.timezone.utc)).isoformat()
    return {"fetched_at": fetched_at, "prices": prices}


def refresh_once():
    data = price_file(fetch_prices())
    if not data["prices"]:
        log.warning("No prices returned; the pages keep their last ones")
        return
    NETWORK_DIR.mkdir(parents=True, exist_ok=True)
    # Kept beside the snapshots so the next site build copies it, and written
    # into the live site now so open pages see it within a minute
    _write_json(NETWORK_DIR / "prices.json", data)
    status = SITE_DIR / "status"
    if SITE_DIR.exists():
        status.mkdir(exist_ok=True)
        _write_json(status / "prices.json", data)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--loop", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    seconds = SETTINGS.live_price_seconds
    if args.loop and seconds <= 0:
        log.info("Live prices are switched off (LIVE_PRICE_SECONDS=0)")
        return
    while True:
        try:
            refresh_once()
        except Exception:
            # A failed refresh must never stop the next one
            log.exception("Price refresh failed")
        if not args.loop:
            return
        time.sleep(seconds)


if __name__ == "__main__":
    main()
