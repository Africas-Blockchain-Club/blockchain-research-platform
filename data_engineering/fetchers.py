import os
import time
import urllib.parse
from email.utils import parsedate_to_datetime

import requests
from defusedxml import ElementTree as DefusedET

MAX_FEED_BYTES = 2_000_000


# ====================== COINGECKO ======================

def _coingecko_get(url, headers, timeout=12, attempts=3):
    """GET from CoinGecko, waiting and retrying when it rate-limits (HTTP 429).
    The free tier allows only a few requests a minute; a short wait recovers
    most limits, and a final 429 is returned to the caller to report."""
    resp = None
    for attempt in range(attempts):
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 429:
            return resp
        wait = min(int(resp.headers.get("Retry-After") or 0) or 15 * (attempt + 1), 60)
        if attempt < attempts - 1:
            time.sleep(wait)
    return resp


# CoinGecko categories that say something about consensus
CONSENSUS_TAGS = ("Proof of Work (PoW)", "Proof of Stake (PoS)", "Cosmos Ecosystem")


def fetch_asset_platforms():
    """CoinGecko's platforms (the chains tokens live on): {id: {"name", "native_coin_id"}},
    or {} when CoinGecko cannot be asked."""
    try:
        headers = {}
        api_key = os.getenv("COINGECKO_API_KEY", "")
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        resp = _coingecko_get("https://api.coingecko.com/api/v3/asset_platforms", headers)
        if resp.status_code != 200:
            return {}
        return {p["id"]: {"name": p.get("name") or p["id"], "native_coin_id": p.get("native_coin_id")}
                for p in resp.json() if p.get("id")}
    except Exception:
        return {}


def _best_search_match(coins, query):
    """The coin whose full name, CoinGecko id or ticker is exactly what was
    typed, so "Celestia" and "TIA" both find Celestia. Several matches go to
    the highest market cap rank: an impostor copying a name or ticker ranks
    far below the real coin."""
    wanted = " ".join(query.split()).casefold()
    matches = [c for c in coins
               if wanted in {(c.get(k) or "").casefold() for k in ("name", "id", "symbol")}]
    if not matches:
        return None
    return min(matches, key=lambda c: c.get("market_cap_rank") or float("inf"))


def fetch_coingecko_data(token, coin_id=None):
    """
    Fetch full market data, community stats, and description from CoinGecko.
    token: a ticker or a full name, for example TIA or Celestia.
    coin_id: CoinGecko's id when it is already known (the featured chains),
    which saves the search request and halves the load on the rate limit.
    """
    try:
        headers = {}
        api_key = os.getenv("COINGECKO_API_KEY", "")
        if api_key:
            headers["x-cg-demo-api-key"] = api_key

        if not coin_id:
            # Resolve the name or ticker to a CoinGecko id
            query = urllib.parse.quote(token.lower())
            search_resp = _coingecko_get(f"https://api.coingecko.com/api/v3/search?query={query}", headers)
            if search_resp.status_code != 200:
                return {"error": f"CoinGecko search returned {search_resp.status_code}"}
            match = _best_search_match(search_resp.json().get("coins", []), token)
            if not match:
                return {"error": f"'{token}' not found on CoinGecko"}
            coin_id = match["id"]

        # Step 2: fetch full data
        data_resp = _coingecko_get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            "?localization=false&tickers=false&market_data=true"
            "&community_data=true&developer_data=false&sparkline=false",
            headers,
        )
        if data_resp.status_code != 200:
            return {"error": f"CoinGecko data endpoint returned {data_resp.status_code}"}

        d = data_resp.json()
        market = d.get("market_data", {})
        community = d.get("community_data", {})

        links = d.get("links", {})
        # Extract social handles for use by the free social fetchers
        twitter_handle = links.get("twitter_screen_name") or ""
        subreddit_url = links.get("subreddit_url") or ""
        # Parse subreddit name from URL e.g. https://www.reddit.com/r/ethereum/
        subreddit_name = ""
        if subreddit_url:
            parts = [p for p in subreddit_url.rstrip("/").split("/") if p]
            if "r" in parts:
                idx = parts.index("r")
                if idx + 1 < len(parts):
                    subreddit_name = parts[idx + 1]

        return {
            "id": coin_id,
            "name": d.get("name"),
            "symbol": d.get("symbol", "").upper(),
            "description": (d.get("description", {}).get("en") or "")[:600],
            "categories": d.get("categories", [])[:5],
            # Clues to how the chain reaches agreement, for the attack cost page
            "asset_platform_id": d.get("asset_platform_id"),
            "hashing_algorithm": d.get("hashing_algorithm"),
            "consensus_tags": [c for c in d.get("categories") or [] if c in CONSENSUS_TAGS],
            "price_usd": market.get("current_price", {}).get("usd"),
            "market_cap_usd": market.get("market_cap", {}).get("usd"),
            "fully_diluted_valuation_usd": market.get("fully_diluted_valuation", {}).get("usd"),
            "24h_change_pct": market.get("price_change_percentage_24h"),
            "7d_change_pct": market.get("price_change_percentage_7d"),
            "30d_change_pct": market.get("price_change_percentage_30d"),
            "ath_usd": market.get("ath", {}).get("usd"),
            "ath_change_pct": market.get("ath_change_percentage", {}).get("usd"),
            "total_volume_24h_usd": market.get("total_volume", {}).get("usd"),
            "total_supply": market.get("total_supply"),
            "circulating_supply": market.get("circulating_supply"),
            "max_supply": market.get("max_supply"),
            # Contract addresses by chain: the reliable way to find the real exchange pools
            "platforms": {k: v for k, v in (d.get("platforms") or {}).items() if k and v},
            # CoinGecko community data (sometimes null - fetchers below fill the gap)
            "twitter_followers": community.get("twitter_followers"),
            "twitter_screen_name": twitter_handle,
            "reddit_subscribers": community.get("reddit_subscribers"),
            "subreddit_name": subreddit_name,
            "source": "CoinGecko API",
        }
    except Exception as e:
        return {"error": f"CoinGecko fetch failed: {str(e)}"}


# Depth is self-reported by each exchange, and CoinGecko stopped sending its trust
# rating in 2026, so only large, long-established exchanges count (CoinGecko market
# identifiers, checked 19 October 2026). A small exchange quoting deep books it
# does not have would otherwise make a thin market look deep.
DEPTH_EXCHANGES = {
    "binance", "gdax", "kraken", "okex", "bybit_spot", "bitstamp", "upbit", "bithumb",
    "bitget", "kucoin", "gemini", "crypto_com", "bitvavo", "gate", "valr", "luno",
}


def fetch_market_depth(coin_id):
    """
    Order-book depth across the exchanges CoinGecko tracks: how many US Dollars
    of selling (or buying) it would take to move the price by 2% on each market,
    added up. This is the liquidity measure for coins that trade mostly on
    centralised exchanges, where one DEX pool says little.
    """
    if not coin_id:
        return {"error": "No CoinGecko id, so market depth cannot be read"}
    headers = {}
    if os.getenv("COINGECKO_API_KEY"):
        headers["x-cg-demo-api-key"] = os.getenv("COINGECKO_API_KEY")
    try:
        resp = _coingecko_get(
            f"https://api.coingecko.com/api/v3/coins/{urllib.parse.quote(coin_id)}/tickers"
            "?depth=true&order=volume_desc",
            headers,
        )
        if resp.status_code != 200:
            return {"error": f"CoinGecko tickers returned {resp.status_code}", "failed": True}
        markets = [
            t for t in resp.json().get("tickers") or []
            if (t.get("market") or {}).get("identifier") in DEPTH_EXCHANGES
            and not t.get("is_anomaly") and not t.get("is_stale")
            and isinstance(t.get("cost_to_move_down_usd"), (int, float))
        ]
        if not markets:
            return {"error": "None of the large exchanges reported order-book depth for this coin"}
        markets.sort(key=lambda t: t["cost_to_move_down_usd"], reverse=True)
        return {
            "depth_down_2pct_usd": sum(t["cost_to_move_down_usd"] for t in markets),
            "depth_up_2pct_usd": sum(t.get("cost_to_move_up_usd") or 0 for t in markets),
            "markets_counted": len(markets),
            "deepest_markets": [
                {"exchange": (t.get("market") or {}).get("name"), "pair": f"{t.get('base')}/{t.get('target')}",
                 "depth_down_2pct_usd": t["cost_to_move_down_usd"]}
                for t in markets[:5]
            ],
            "source": "CoinGecko exchange tickers (large established exchanges only, current markets)",
        }
    except Exception as e:
        return {"error": f"CoinGecko tickers error: {e}", "failed": True}


# ====================== SOCIAL STATS ======================

def fetch_reddit_stats(subreddit_name):
    """
    Fetch Reddit subscriber count using the free OAuth app-only flow.
    No user login required; only a free Reddit app registration.
    Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env:
      1. Go to reddit.com/prefs/apps
      2. Click 'create an app' -> choose 'script'
      3. Copy the client id (under the app name) and secret
    """
    if not subreddit_name:
        return {"error": "No subreddit name"}
    subreddit = subreddit_name.strip("/").lstrip("r/")

    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        return {"error": "REDDIT_CLIENT_ID/SECRET not set - see .env.example"}

    try:
        # App-only OAuth - no user credentials needed
        token_resp = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=requests.auth.HTTPBasicAuth(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": "ABCResearch/1.0"},
            timeout=8,
        )
        if token_resp.status_code != 200:
            return {"error": f"Reddit OAuth token failed: {token_resp.status_code}"}

        token = token_resp.json().get("access_token")
        about_resp = requests.get(
            f"https://oauth.reddit.com/r/{subreddit}/about",
            headers={"Authorization": f"Bearer {token}", "User-Agent": "ABCResearch/1.0"},
            timeout=8,
        )
        if about_resp.status_code == 200:
            d = about_resp.json().get("data", {})
            return {
                "subscribers": d.get("subscribers", 0),
                "active_users": d.get("accounts_active", 0),
                "source": "Reddit OAuth API (free)",
            }
        return {"error": f"Reddit about returned {about_resp.status_code}"}
    except Exception as e:
        return {"error": f"Reddit fetch failed: {str(e)}"}


def fetch_cryptocompare_social(symbol):
    """
    Placeholder - CryptoCompare removed social data from their free tier.
    Kept for future use if a paid key is added (CRYPTOCOMPARE_API_KEY in .env).
    """
    api_key = os.getenv("CRYPTOCOMPARE_API_KEY", "")
    if not api_key:
        return {"error": "CRYPTOCOMPARE_API_KEY not set - social data requires paid tier"}
    return {"error": "CryptoCompare social data not available on free tier"}


def check_cmc_listed(token):
    """Quick CMC listing check. True on HTTP 200, False on 404, and None when
    the check itself failed: an outage must never read as "not listed"."""
    try:
        resp = requests.get(
            f"https://coinmarketcap.com/currencies/{token.lower()}/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            return False
        return None
    except Exception:
        return None


# ====================== EXCHANGE RATE ======================

def fetch_usd_zar():
    """Live USD to ZAR rate, read from CoinGecko's USDC price in Rand.
    Returns (rate, source) or (None, reason) so the caller can fall back
    loudly to the configured rate."""
    try:
        headers = {}
        api_key = os.getenv("COINGECKO_API_KEY", "")
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "usd-coin", "vs_currencies": "zar"},
            headers=headers,
            timeout=8,
        )
        resp.raise_for_status()
        rate = resp.json().get("usd-coin", {}).get("zar")
        if rate:
            return float(rate), "CoinGecko (USD Coin, a stablecoin worth one US Dollar, priced in South African Rand)"
        return None, "CoinGecko returned no ZAR rate"
    except Exception as e:
        return None, f"Exchange rate fetch failed: {e}"


# ====================== NEWS HEADLINES (Google News RSS) ======================

def fetch_cryptopanic_news(token):
    """
    Fetch recent news headlines for a token using Google News RSS.
    No API key required. Returns a list of {title, source, published_at}.
    Uses the token symbol + known full name (from CoinGecko if available) for best results.
    """
    # Map common symbols to full names for a better search query
    KNOWN_NAMES = {
        "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "BNB": "BNB",
        "ADA": "Cardano", "ENA": "Ethena", "OP": "Optimism", "ARB": "Arbitrum",
        "LINK": "Chainlink", "DOT": "Polkadot", "AVAX": "Avalanche",
        "UNI": "Uniswap", "AAVE": "Aave", "MKR": "Maker",
        "XRP": "XRP Ledger", "HYPE": "Hyperliquid",
    }
    full_name = KNOWN_NAMES.get(token.upper(), token)
    query = urllib.parse.quote(f"{full_name} {token.upper()} crypto")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        if len(resp.content) > MAX_FEED_BYTES:
            raise ValueError(f"news feed larger than {MAX_FEED_BYTES} bytes")
        # A hardened XML parser: no entity expansion, no external entities, and no
        # hand-written regular expressions over text someone else controls
        channel = DefusedET.fromstring(resp.content).find("channel")
        headlines = []
        for item in (channel.findall("item") if channel is not None else [])[:12]:
            raw_title = (item.findtext("title") or "").strip()
            if not raw_title:
                continue
            # Google News appends " - Source Name"; split it off
            parts = raw_title.rsplit(" - ", 1)
            source = parts[1].strip() if len(parts) == 2 else (item.findtext("source") or "Unknown").strip()
            headlines.append({
                "title": parts[0].strip(),
                "source": source,
                "published_at": (item.findtext("pubDate") or "").strip(),
            })

        def _parse_date(h):
            try:
                return parsedate_to_datetime(h["published_at"])
            except Exception:
                return None

        headlines.sort(key=lambda h: (_parse_date(h) is not None, _parse_date(h)), reverse=True)
        return headlines if headlines else [{"note": f"No news found for {token}."}]
    except Exception as e:
        return [{"error": f"News fetch failed: {str(e)}"}]


# ====================== DEXSCREENER ======================

# Native coins have no contract of their own; their DEX pools trade the wrapped
# version. Addresses checked against DexScreener on 18 October 2026.
NATIVE_WRAPPED = {
    "SOL": [("solana", "So11111111111111111111111111111111111111112")],
    "ETH": [("ethereum", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")],
    "BNB": [("bsc", "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")],
    "AVAX": [("avalanche", "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")],
}

# CoinGecko platform names that differ from DexScreener chain ids
_CG_TO_DEXSCREENER = {
    "binance-smart-chain": "bsc",
    "arbitrum-one": "arbitrum",
    "polygon-pos": "polygon",
    "optimistic-ethereum": "optimism",
}


def token_contracts(token, coingecko_platforms=None):
    """Return [(dexscreener_chain, address), ...] for a token: the wrapped
    contract for a native coin, otherwise the addresses CoinGecko publishes."""
    if token.upper() in NATIVE_WRAPPED:
        return NATIVE_WRAPPED[token.upper()]
    return [(_CG_TO_DEXSCREENER.get(chain, chain), address)
            for chain, address in (coingecko_platforms or {}).items()]


def _pair_summary(pair, match):
    info = pair.get("info", {})
    # An order-book exchange (Hyperliquid's own spot market, for example) has no
    # pool, so DexScreener sends no liquidity at all. That is missing data, not
    # an empty pool, and must never be reported as zero.
    liquidity = pair.get("liquidity") or {}
    return {
        "price_usd": pair.get("priceUsd"),
        "market_cap": pair.get("fdv"),
        "volume_24h": pair.get("volume", {}).get("h24", 0),
        "liquidity_usd": liquidity.get("usd"),
        "liquidity_base": liquidity.get("base"),
        "liquidity_quote": liquidity.get("quote"),
        "liquidity_reported": bool(liquidity),
        "dex": pair.get("dexId"),
        "chain": pair.get("chainId"),
        "pair_address": pair.get("pairAddress"),
        "base_token": pair.get("baseToken", {}).get("symbol"),
        "base_token_address": pair.get("baseToken", {}).get("address"),
        "quote_token": pair.get("quoteToken", {}).get("symbol"),
        "name": pair.get("baseToken", {}).get("name"),
        "social_links": [s.get("url") for s in info.get("socials", [])],
        "website_links": [w.get("url") for w in info.get("websites", [])],
        "url": pair.get("url"),
        "match": match,
    }


def _deepest_active(pairs):
    """Deepest pool among those that actually traded today. Idle pools with
    huge balances are usually impostor tokens or abandoned."""
    active = [p for p in pairs if float((p.get("volume") or {}).get("h24", 0) or 0) > 0]
    return max(active or pairs, key=lambda p: float((p.get("liquidity") or {}).get("usd", 0) or 0))


def fetch_dexscreener_data(token, contracts=None, reference_price=None):
    """
    Fetch the main DEX pool for a token from DexScreener.

    With contracts (from token_contracts()), only pools whose base token is
    one of those exact contracts count. Searching by ticker alone returns
    impostor tokens: on 18 October 2026 a search for SOL returned pools of
    fake "SOL" tokens claiming $2.5bn of liquidity. The ticker search is kept
    only as a labelled fallback, filtered to pools priced within 10% of the
    reference price from CoinGecko.
    """
    try:
        if contracts:
            wanted = {(chain, address.lower()) for chain, address in contracts}
            addresses = ",".join(address for _, address in contracts[:30])
            resp = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{addresses}", timeout=10)
            if resp.status_code != 200:
                return {"error": f"DexScreener returned {resp.status_code}"}
            pairs = [
                p for p in resp.json().get("pairs") or []
                if (p.get("chainId"), (p.get("baseToken") or {}).get("address", "").lower()) in wanted
            ]
            if not pairs:
                return {"error": "No exchange pool found for this token's contract addresses"}
            return _pair_summary(_deepest_active(pairs), "contract address published by CoinGecko")

        resp = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={token.upper()}", timeout=10)
        if resp.status_code != 200:
            return {"error": f"DexScreener returned {resp.status_code}"}
        pairs = [p for p in resp.json().get("pairs") or []
                 if (p.get("baseToken") or {}).get("symbol", "").upper() == token.upper()]
        reference = float(reference_price or 0)
        if reference > 0:
            pairs = [p for p in pairs if abs(float(p.get("priceUsd") or 0) / reference - 1) <= 0.10]
        if not pairs:
            return {"error": "Token not found on DexScreener"}
        return _pair_summary(_deepest_active(pairs), "ticker search only; the contract could not be confirmed")
    except Exception as e:
        return {"error": f"DexScreener API error: {str(e)}"}


# ====================== COINGLASS (DERIVATIVES) ======================

def fetch_coinglass_data(token, api_key=None):
    """Fetch open interest and volume from Coinglass."""
    api_key = api_key or os.getenv("COINGLASS_API_KEY")
    if not api_key:
        return {"error": "COINGLASS_API_KEY not set"}
    try:
        resp = requests.get(
            f"https://open-api.coinglass.com/public/v2/open_interest?symbol={token.upper()}",
            headers={"coinglassSecret": api_key},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            return {
                "open_interest": data.get("openInterest", 0),
                "open_interest_amount": data.get("openInterestAmount", 0),
                "vol_usd": data.get("volUsd", 0),
            }
        return {"error": f"Coinglass returned {resp.status_code}"}
    except Exception as e:
        return {"error": f"Coinglass error: {str(e)}"}


def fetch_liquidation_data(token, api_key=None):
    """Fetch 4-hour liquidation heatmap data from Coinglass."""
    api_key = api_key or os.getenv("COINGLASS_API_KEY")
    if not api_key:
        return {"error": "COINGLASS_API_KEY not set"}
    try:
        resp = requests.get(
            f"https://open-api.coinglass.com/public/v2/liquidation_info?symbol={token.upper()}&time_type=h4",
            headers={"coinglassSecret": api_key},
            timeout=10,
        )
        if resp.status_code == 200:
            return {"liquidation_levels": resp.json().get("data", []), "source": "Coinglass"}
        return {"error": f"Coinglass liquidation returned {resp.status_code}"}
    except Exception as e:
        return {"error": f"Coinglass liquidation error: {str(e)}"}


# ====================== ULTRASOUND / TREASURIES ======================

def fetch_ultrasound_data(token):
    """Fetch ETH burn and issuance data from ultrasound.money."""
    if token.lower() != "eth":
        return {"error": "Ultrasound data only available for ETH"}
    try:
        resp = requests.get("https://api.ultrasound.money/v2/fees/1d", timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            return {
                "daily_burn": d.get("daily_burn", 0),
                "daily_issuance": d.get("daily_issuance", 0),
                "net_supply_change": d.get("net_supply_change", 0),
                "timestamp": d.get("timestamp"),
            }
    except Exception as e:
        return {"error": f"Ultrasound API error: {str(e)}"}


def fetch_treasuries(token):
    """Return known institutional BTC treasury data."""
    if token.lower() not in ["btc", "eth"]:
        return []
    if token.lower() == "eth":
        return [{"entity": "Ethereum Foundation", "holdings": "Unknown", "notes": "No direct treasury tracking"}]
    try:
        resp = requests.get("https://api.treasury.gov/v1/debt/top/top_100_holders.json", timeout=10)
        if resp.status_code == 200:
            items = resp.json()
            return [i for i in items if "bitcoin" in str(i).lower() or "crypto" in str(i).lower()][:5]
    except Exception as e:
        return [{"error": f"Treasury fetch failed: {str(e)}"}]
    return []


# ====================== DEFILLAMA ======================

def fetch_defillama_data(token, name=None):
    """TVL from DefiLlama, for a chain (when the token is a chain's native
    asset) or a protocol. Several protocols can share one ticker, so a
    protocol is matched on its name first and on its symbol only as a
    labelled fallback; the old symbol-only match reported "Solana Farm"
    (TVL $225) as SOL."""
    try:
        chains = requests.get("https://api.llama.fi/v2/chains", timeout=15)
        if chains.status_code == 200:
            for c in chains.json():
                if (c.get("tokenSymbol") or "").upper() == token.upper():
                    return {
                        "kind": "chain",
                        "name": c.get("name"),
                        "tvl_usd": c.get("tvl"),
                        "match": "native token of this chain",
                        "source": "DefiLlama API",
                    }

        resp = requests.get("https://api.llama.fi/protocols", timeout=15)
        if resp.status_code != 200:
            return {"error": f"DefiLlama returned {resp.status_code}"}
        matches = [p for p in resp.json() if (p.get("symbol") or "").upper() == token.upper()]
        if not matches:
            return {"note": f"{token} is not tracked as a chain or DeFi protocol on DefiLlama."}
        by_name = [p for p in matches if name and (p.get("name") or "").lower() == name.lower()]
        best = by_name[0] if by_name else max(matches, key=lambda p: p.get("tvl") or 0)
        return {
            "kind": "protocol",
            "name": best.get("name"),
            "tvl_usd": best.get("tvl"),
            "category": best.get("category"),
            "chains": ", ".join(best.get("chains") or []),
            "match": "protocol name" if by_name else f"ticker only ({len(matches)} protocols use this ticker; check this is the right one)",
            "source": "DefiLlama API",
        }
    except Exception as e:
        return {"error": f"DefiLlama error: {str(e)}"}


# ====================== SCREENSHOT BOT (re-exported) ======================
# Keeping this import path consistent for report_generator.py
