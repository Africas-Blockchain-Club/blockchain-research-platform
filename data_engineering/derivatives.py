"""
Open interest on perpetual futures, from the exchanges' own free public APIs.

Coinglass (fetchers.fetch_coinglass_data) needs a paid key. Without one, this
adapter asks four large venues directly (OKX, Bitget, Gate, Hyperliquid) and adds up what they report, so the
leverage check has data. It never raises. Each venue ends in one of three
states:
  ok          the venue lists the contract and reported its open interest
  not listed  the venue answered and has no such contract (a fact, not a fault)
  failed      the venue could not be reached or answered with an error
Only "failed" counts as a source error, so a coin with no futures market is
not reported as a broken source. Every endpoint was checked live on
19 October 2026.
"""
import time

import requests

TIMEOUT = 10
RETRY_SECONDS = 2
HEADERS = {"User-Agent": "blockchain-research-platform"}


class NotListed(Exception):
    """The venue answered, and it has no perpetual contract for this coin."""


def _get(url, **params):
    resp = requests.get(url, params=params, timeout=TIMEOUT, headers=HEADERS)
    if resp.status_code == 400:
        raise NotListed(resp.text[:120])
    resp.raise_for_status()
    return resp.json()


def _bitget(symbol):
    rows = _get("https://api.bitget.com/api/v2/mix/market/ticker", symbol=f"{symbol}USDT",
                productType="usdt-futures").get("data") or []
    if not rows:
        raise NotListed("no contract")
    return float(rows[0]["holdingAmount"]) * float(rows[0]["markPrice"])


def _gate(symbol):
    contract = _get(f"https://api.gateio.ws/api/v4/futures/usdt/contracts/{symbol}_USDT")
    return float(contract["position_size"]) * float(contract["quanto_multiplier"]) * float(contract["mark_price"])


def _okx(symbol):
    data = _get("https://www.okx.com/api/v5/public/open-interest", instType="SWAP", instId=f"{symbol}-USDT-SWAP")
    rows = data.get("data") or []
    if data.get("code") != "0" or not rows:
        raise NotListed(data.get("msg") or "no contract")
    return float(rows[0]["oiUsd"])


def _hyperliquid(symbol):
    resp = requests.post("https://api.hyperliquid.xyz/info", json={"type": "metaAndAssetCtxs"},
                         timeout=TIMEOUT, headers=HEADERS)
    resp.raise_for_status()
    meta, contexts = resp.json()
    names = [asset["name"] for asset in meta["universe"]]
    if symbol not in names:
        raise NotListed("no contract")
    ctx = contexts[names.index(symbol)]
    return float(ctx["openInterest"]) * float(ctx["markPx"])


# Binance and Bybit are not used: both refuse requests from cloud servers (HTTP 451
# and 403 from Fly's Johannesburg machines and GitHub's runners, 19 October 2026).
VENUES = (("OKX", _okx), ("Bitget", _bitget), ("Gate", _gate), ("Hyperliquid", _hyperliquid))


def fetch_open_interest(symbol):
    """Open interest in US Dollars on USDT-margined perpetuals at four venues.
    Returns {"open_interest", "venues", "not_listed", "failed", "source"}, or
    {"error", ...} when no venue reported a figure."""
    symbol = (symbol or "").upper()
    venues, not_listed, failed = {}, [], {}
    for name, read in VENUES:
        for attempt in (1, 2):
            try:
                venues[name] = read(symbol)
                failed.pop(name, None)
                break
            except NotListed:
                not_listed.append(name)
                break
            except Exception as e:
                # One retry: a single dropped connection is not a venue failing
                failed[name] = f"{type(e).__name__}: {e}"[:120]
                if attempt == 1:
                    time.sleep(RETRY_SECONDS)
    result = {"venues": venues, "not_listed": not_listed, "failed": failed,
              "source": "OKX, Bitget, Gate and Hyperliquid public futures APIs (USDT-margined perpetuals)"}
    if not venues:
        result["error"] = ("No perpetual futures market found at OKX, Bitget, Gate or Hyperliquid"
                           if not failed else "Futures venues could not be read: " + ", ".join(failed))
        return result
    result["open_interest"] = sum(venues.values())
    return result
