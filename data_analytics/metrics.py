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
