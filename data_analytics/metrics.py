def compute_derived_metrics(dex_data, token):
    """
    Computes liquidity and basic standard metrics from raw dex data.
    """
    market_cap = float(dex_data.get("market_cap") or 0)
    volume_24h = float(dex_data.get("volume_24h") or 0)
    liquidity_usd = float(dex_data.get("liquidity_usd") or 0)
    liquidity_base = float(dex_data.get("liquidity_base") or 0)
    liquidity_quote = float(dex_data.get("liquidity_quote") or 0)
    
    liquidity_turnover_ratio = round(volume_24h / market_cap * 100, 4) if market_cap > 0 else 0
    depth_to_mcap_ratio = round(liquidity_usd / market_cap * 100, 4) if market_cap > 0 else 0

    return {
        "market_cap": market_cap,
        "volume_24h": volume_24h,
        "liquidity_usd": liquidity_usd,
        "liquidity_base": liquidity_base,
        "liquidity_quote": liquidity_quote,
        "liquidity_turnover_ratio": liquidity_turnover_ratio,
        "depth_to_mcap_ratio": depth_to_mcap_ratio
    }

def compute_kill_switch_flags(token_info):
    """
    Compute the 4 Kill Switch red-flag checks from available data.
    Returns a dict of flag_name -> {triggered: bool, value: ..., reason: str}
    """
    flags = {}
    market_cap = token_info.get("market_cap", 0) or 0
    volume_24h = token_info.get("volume_24h", 0) or 0
    liquidity_usd = token_info.get("liquidity_usd", 0) or 0

    # 1. Wash Trading: Volume/MCap ratio > 1.0
    if market_cap > 0:
        vol_mcap_ratio = volume_24h / market_cap
        flags["wash_trading"] = {
            "triggered": vol_mcap_ratio > 1.0,
            "value": round(vol_mcap_ratio, 4),
            "reason": f"Volume/Market Cap ratio = {vol_mcap_ratio:.4f}. Ratio > 1.0 indicates potential wash trading (fake demand)."
        }
    else:
        flags["wash_trading"] = {"triggered": False, "value": None, "reason": "Market cap data unavailable."}

    # 2. Thin Order Books (flagged if data available from liquidity tickers)
    if market_cap > 100_000_000:
        # Rough proxy: if liquidity in AMM is very low relative to MCap
        flags["thin_order_books"] = {
            "triggered": liquidity_usd < 500_000,
            "value": liquidity_usd,
            "reason": f"DEX Liquidity = ${liquidity_usd:,.0f}. For a >${market_cap/1e6:.0f}M MCap token, depth < $500k signals a liquidity trap."
        }
    else:
        # Smaller tokens naturally have less liquidity, but let's check ratio
        flags["thin_order_books"] = {
            "triggered": liquidity_usd < (market_cap * 0.005) and market_cap > 0, # Trigger if liqudity is < 0.5% of FDV
            "value": liquidity_usd,
            "reason": f"DEX Liquidity = ${liquidity_usd:,.0f} relative to ${market_cap:,.0f} FDV. Less than 0.5% depth signals high slippage risk."
        }

    # 3. Supply Unlock Cliff (>15% unlocking in 30 days)
    # Since we can't fetch unlocks easily from standard free APIs, we defer to AI or note failure
    flags["supply_unlock_cliff"] = {
        "triggered": False,
        "value": None,
        "reason": "Supply unlock schedule requires TokenUnlocks.app data. Flagged for AI narrative assessment."
    }

    # 4. Concentration Risk (top 10 wallets >80%)
    flags["concentration_risk"] = {
        "triggered": False,
        "value": None,
        "reason": "Requires on-chain wallet distribution data (Arkham/Nansen). Flagged for AI narrative assessment."
    }

    return flags
