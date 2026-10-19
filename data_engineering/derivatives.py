"""
Open interest on perpetual futures, from the exchanges' own free public APIs.

Coinglass (fetchers.fetch_coinglass_data) needs a paid key. Without one, this
adapter asks four large venues directly and adds up what they report, so the
leverage check has data. It never raises. Each venue ends in one of three
states:
  ok          the venue lists the contract and reported its open interest
  not listed  the venue answered and has no such contract (a fact, not a fault)
  failed      the venue could not be reached or answered with an error
Only "failed" counts as a source error, so a coin with no futures market is
not reported as a broken source. Every endpoint was checked live on
19 October 2026.
"""
import requests

TIMEOUT = 10
HEADERS = {"User-Agent": "blockchain-research-platform"}


class NotListed(Exception):
    """The venue answered, and it has no perpetual contract for this coin."""


def _get(url, **params):
    resp = requests.get(url, params=params, timeout=TIMEOUT, headers=HEADERS)
    if resp.status_code == 400:
        raise NotListed(resp.text[:120])
    resp.raise_for_status()
    return resp.json()


def _binance(symbol):
    pair = f"{symbol}USDT"
    contracts = float(_get("https://fapi.binance.com/fapi/v1/openInterest", symbol=pair)["openInterest"])
    mark = float(_get("https://fapi.binance.com/fapi/v1/premiumIndex", symbol=pair)["markPrice"])
    return contracts * mark


def _bybit(symbol):
    data = _get("https://api.bybit.com/v5/market/tickers", category="linear", symbol=f"{symbol}USDT")
    rows = (data.get("result") or {}).get("list") or []
    if data.get("retCode") != 0 or not rows:
        raise NotListed(data.get("retMsg") or "no contract")
    return float(rows[0]["openInterestValue"])


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


VENUES = (("Binance", _binance), ("Bybit", _bybit), ("OKX", _okx), ("Hyperliquid", _hyperliquid))


def fetch_open_interest(symbol):
    """Open interest in US Dollars on USDT-margined perpetuals at four venues.
    Returns {"open_interest", "venues", "not_listed", "failed", "source"}, or
    {"error", ...} when no venue reported a figure."""
    symbol = (symbol or "").upper()
    venues, not_listed, failed = {}, [], {}
    for name, read in VENUES:
        try:
            venues[name] = read(symbol)
        except NotListed:
            not_listed.append(name)
        except Exception as e:
            failed[name] = f"{type(e).__name__}: {e}"[:120]
    result = {"venues": venues, "not_listed": not_listed, "failed": failed,
              "source": "Binance, Bybit, OKX and Hyperliquid public futures APIs (USDT-margined perpetuals)"}
    if not venues:
        result["error"] = ("No perpetual futures market found at Binance, Bybit, OKX or Hyperliquid"
                           if not failed else "Futures venues could not be read: " + ", ".join(failed))
        return result
    result["open_interest"] = sum(venues.values())
    return result
