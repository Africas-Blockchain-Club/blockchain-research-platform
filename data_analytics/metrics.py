from data_analytics.formatting import to_float


def compute_derived_metrics(dex_data, token):
    """
    Computes liquidity and basic standard metrics from raw dex data.
    A figure the source did not report stays None, so it reads as "No data"
    downstream instead of as an empty pool.
    """
    market_cap = to_float(dex_data.get("market_cap")) or 0
    # No pool at all (an error from DexScreener) is no data, not a pool with no trading
    volume_24h = to_float(dex_data.get("volume_24h"))
    liquidity_usd = to_float(dex_data.get("liquidity_usd"))
    liquidity_base = to_float(dex_data.get("liquidity_base"))
    liquidity_quote = to_float(dex_data.get("liquidity_quote"))

    liquidity_turnover_ratio = (round(volume_24h / market_cap * 100, 4)
                                if market_cap > 0 and volume_24h is not None else None)
    depth_to_mcap_ratio = (round(liquidity_usd / market_cap * 100, 4)
                           if market_cap > 0 and liquidity_usd is not None else None)

    return {
        "market_cap": market_cap,
        "volume_24h": volume_24h,
        "liquidity_usd": liquidity_usd,
        "liquidity_base": liquidity_base,
        "liquidity_quote": liquidity_quote,
        "liquidity_turnover_ratio": liquidity_turnover_ratio,
        "depth_to_mcap_ratio": depth_to_mcap_ratio
    }
