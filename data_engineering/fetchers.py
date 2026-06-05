import requests
import re
import os
import urllib.request
import urllib.parse


# ====================== COINGECKO ======================

def fetch_coingecko_data(token):
    """
    Fetch full market data, community stats, and description from CoinGecko.
    Replaces the old listing-check with a real data pull.
    """
    try:
        headers = {}
        api_key = os.getenv("COINGECKO_API_KEY", "")
        if api_key:
            headers["x-cg-demo-api-key"] = api_key

        # Step 1: resolve token symbol → CoinGecko ID
        search_resp = requests.get(
            f"https://api.coingecko.com/api/v3/search?query={token.lower()}",
            headers=headers,
            timeout=10,
        )
        if search_resp.status_code != 200:
            return {"error": f"CoinGecko search returned {search_resp.status_code}"}

        coins = search_resp.json().get("coins", [])
        # Prefer an exact symbol match; fall back to the first result
        exact = [c for c in coins if c.get("symbol", "").upper() == token.upper()]
        if not exact:
            return {"error": f"Token '{token}' not found on CoinGecko"}
        coin_id = exact[0]["id"]

        # Step 2: fetch full data
        data_resp = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            "?localization=false&tickers=false&market_data=true"
            "&community_data=true&developer_data=false&sparkline=false",
            headers=headers,
            timeout=12,
        )
        if data_resp.status_code != 200:
            return {"error": f"CoinGecko data endpoint returned {data_resp.status_code}"}

        d = data_resp.json()
        market = d.get("market_data", {})
        community = d.get("community_data", {})

        return {
            "id": coin_id,
            "name": d.get("name"),
            "symbol": d.get("symbol", "").upper(),
            "description": (d.get("description", {}).get("en") or "")[:600],
            "categories": d.get("categories", [])[:5],
            "price_usd": market.get("current_price", {}).get("usd"),
            "market_cap_usd": market.get("market_cap", {}).get("usd"),
            "fully_diluted_valuation_usd": market.get("fully_diluted_valuation", {}).get("usd"),
            "24h_change_pct": market.get("price_change_percentage_24h"),
            "7d_change_pct": market.get("price_change_percentage_7d"),
            "30d_change_pct": market.get("price_change_percentage_30d"),
            "ath_usd": market.get("ath", {}).get("usd"),
            "ath_change_pct": market.get("ath_change_percentage", {}).get("usd"),
            "total_supply": market.get("total_supply"),
            "circulating_supply": market.get("circulating_supply"),
            "max_supply": market.get("max_supply"),
            "twitter_followers": community.get("twitter_followers"),
            "reddit_subscribers": community.get("reddit_subscribers"),
            "source": "CoinGecko API",
        }
    except Exception as e:
        return {"error": f"CoinGecko fetch failed: {str(e)}"}


def check_cmc_listed(token):
    """Quick CMC listing check. Returns True on HTTP 200."""
    try:
        resp = requests.get(
            f"https://coinmarketcap.com/currencies/{token.lower()}/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False


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
    }
    full_name = KNOWN_NAMES.get(token.upper(), token)
    query = urllib.parse.quote(f"{full_name} {token.upper()} crypto")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        xml = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")

        # Extract individual <item> blocks
        items = re.findall(r"<item>(.*?)</item>", xml, re.DOTALL)
        headlines = []
        for item in items[:12]:
            title_m = re.search(r"<title>(.*?)</title>", item, re.DOTALL)
            date_m = re.search(r"<pubDate>(.*?)</pubDate>", item, re.DOTALL)
            source_m = re.search(r'<source[^>]*>(.*?)</source>', item, re.DOTALL)
            if not title_m:
                continue
            raw_title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
            # Google News appends " - Source Name"; split it off
            parts = raw_title.rsplit(" - ", 1)
            title = parts[0].strip()
            source = parts[1].strip() if len(parts) == 2 else (source_m.group(1).strip() if source_m else "Unknown")
            headlines.append({
                "title": title,
                "source": source,
                "published_at": date_m.group(1).strip() if date_m else "",
            })
        return headlines if headlines else [{"note": f"No news found for {token}."}]
    except Exception as e:
        return [{"error": f"News fetch failed: {str(e)}"}]


# ====================== DEXSCREENER ======================

def fetch_dexscreener_data(token):
    """
    Fetch on-chain DEX pair metrics from DexScreener.
    Picks the highest-liquidity pair for the token regardless of chain.
    """
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={token.upper()}"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return {"error": f"DexScreener returned {resp.status_code}"}

        pairs = resp.json().get("pairs", [])
        if not pairs:
            return {"error": "Token not found on DexScreener"}

        # Exact symbol match first, then fall back to all results
        exact = [p for p in pairs if p.get("baseToken", {}).get("symbol", "").upper() == token.upper()]
        candidates = exact if exact else pairs

        # Pick highest-liquidity pair
        candidates.sort(
            key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0),
            reverse=True,
        )
        pair = candidates[0]

        info = pair.get("info", {})
        return {
            "price_usd": pair.get("priceUsd"),
            "market_cap": pair.get("fdv"),
            "volume_24h": pair.get("volume", {}).get("h24", 0),
            "liquidity_usd": pair.get("liquidity", {}).get("usd", 0),
            "liquidity_base": pair.get("liquidity", {}).get("base", 0),
            "liquidity_quote": pair.get("liquidity", {}).get("quote", 0),
            "dex": pair.get("dexId"),
            "chain": pair.get("chainId"),
            "pair_address": pair.get("pairAddress"),
            "base_token": pair.get("baseToken", {}).get("symbol"),
            "quote_token": pair.get("quoteToken", {}).get("symbol"),
            "name": pair.get("baseToken", {}).get("name"),
            "social_links": [s.get("url") for s in info.get("socials", [])],
            "website_links": [w.get("url") for w in info.get("websites", [])],
            "url": pair.get("url"),
        }
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

def fetch_defillama_data(token):
    """Fetch TVL and protocol category from DefiLlama."""
    try:
        resp = requests.get("https://api.llama.fi/protocols", timeout=15)
        if resp.status_code == 200:
            for p in resp.json():
                if p.get("symbol", "").upper() == token.upper():
                    return {
                        "name": p.get("name"),
                        "tvl_usd": p.get("tvl"),
                        "category": p.get("category"),
                        "chains": p.get("chains"),
                        "mcap_usd": p.get("mcap"),
                        "source": "DefiLlama API",
                    }
            return {"note": f"'{token}' not tracked as a DeFi protocol on DefiLlama."}
        return {"error": f"DefiLlama returned {resp.status_code}"}
    except Exception as e:
        return {"error": f"DefiLlama error: {str(e)}"}


# ====================== SCREENSHOT BOT (re-exported) ======================
# Keeping this import path consistent for report_generator.py
