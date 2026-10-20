"""
The risk profile: plain, rule-based checks on a token's public data.

This replaces the old Blueprint Score and Buy/Sell verdict. A score or a
verdict ranks a token as good or bad to own, which is personal financial
advice in most jurisdictions (in South Africa, the FAIS Act). A risk check
does something different: it states a fact, the threshold it was compared
against, and what that kind of finding has meant for other tokens. The
reader draws the conclusion.

Rules for anyone adding a check:
1. Every check has three possible states: flagged, clear, or no data.
   Missing data is never treated as clear.
2. Thresholds are teaching thresholds chosen by this platform. Say so; do
   not present them as industry standards.
3. Explanations describe what a finding means. They never say what to do.
4. No check is weighted against another, and there is no total. Adding the
   checks into one number would recreate a rating.
"""
from data_analytics.formatting import pct, to_float, usd

FLAGGED = "flagged"
CLEAR = "clear"
NO_DATA = "no_data"

STATUS_LABELS = {FLAGGED: "Flagged", CLEAR: "Clear", NO_DATA: "No data"}

# Raise when the checks change, so the featured reports are rebuilt with the new
# checks straight away instead of when they next turn 24 hours old.
# 2: exchange depth, futures open interest from public venues, unmeasurable topics moved out
CHECKS_VERSION = 2


def _check(key, name, status, value, threshold, measures, meaning, source):
    return {
        "key": key,
        "name": name,
        "status": status,
        "value": value,
        "threshold": threshold,
        "measures": measures,
        "meaning": meaning,
        "source": source,
    }


def _ratio(numerator, denominator):
    top, bottom = to_float(numerator), to_float(denominator)
    if top is None or bottom is None or bottom <= 0:
        return None
    return top / bottom


def _artificial_volume(info):
    market_cap = info.get("market_cap_usd")
    volume = info.get("24h_volume_total_all_exchanges_usd") or info.get("24h_volume_dex_pair_usd")
    ratio = _ratio(volume, market_cap)
    status = NO_DATA if ratio is None else (FLAGGED if ratio > 1.0 else CLEAR)
    return _check(
        "artificial_volume",
        "Unusually high trading volume",
        status,
        "N/A" if ratio is None else f"{ratio * 100:,.1f}% of market cap traded in 24 hours",
        "More than 100% of market cap traded in 24 hours",
        "Turnover: 24-hour trading volume divided by market capitalisation.",
        "When more than the whole market cap changes hands in a day, part of that volume is often "
        "wash trading (one party trading with itself to make a token look busy).",
        "CoinGecko, DexScreener",
    )


DEPTH_THRESHOLD_USD = 1_000_000


def _thin_liquidity(summary, info):
    depth = summary.get("market_depth") or {}
    if "depth_down_2pct_usd" in depth:
        # Order-book depth across large exchanges: the right measure for coins that
        # trade mostly on centralised exchanges, which is nearly every chain's coin
        amount = depth["depth_down_2pct_usd"]
        return _check(
            "thin_liquidity",
            "Thin market depth",
            FLAGGED if amount < DEPTH_THRESHOLD_USD else CLEAR,
            f"{usd(amount)} of selling moves the price 2% across {depth.get('markets_counted', 0)} large-exchange markets",
            f"Less than {usd(DEPTH_THRESHOLD_USD)} of selling moves the price 2%",
            "Depth: how many US Dollars of selling it takes to push the price down 2% on each order book, "
            "added up across large, established exchanges. Smaller exchanges are not counted.",
            "Thin depth means a single large sale moves the price sharply (slippage). Deep books absorb "
            "large trades with little price change.",
            "CoinGecko exchange tickers",
        )
    # No exchange depth (a token that trades only on DEXs): fall back to the main pool
    ratio = _ratio(info.get("liquidity_usd"), info.get("market_cap_usd"))
    status = NO_DATA if ratio is None else (FLAGGED if ratio < 0.01 else CLEAR)
    return _check(
        "thin_liquidity",
        "Thin on-chain liquidity",
        status,
        "N/A" if ratio is None else f"{ratio * 100:,.2f}% of market cap in the main decentralised exchange (DEX) pool",
        "Less than 1% of market cap in the main decentralised exchange (DEX) pool",
        "Depth: money in the main decentralised exchange (DEX) pool, divided by market cap. Used only "
        "when no large exchange reports order-book depth for this token.",
        "A thin pool means a single large sale moves the price sharply (slippage).",
        "DexScreener",
    )


def _dilution(info):
    ratio = _ratio(info.get("fully_diluted_valuation_usd"), info.get("market_cap_usd"))
    status = NO_DATA if ratio is None else (FLAGGED if ratio > 3.0 else CLEAR)
    return _check(
        "dilution",
        "Large future supply (dilution)",
        status,
        "N/A" if ratio is None else f"Fully diluted value is {ratio:,.2f} times market cap",
        "Fully diluted value more than 3 times market cap",
        "FDV (fully diluted valuation): the market cap if every token that will ever exist were "
        "already in circulation.",
        "A large gap means many tokens are still to be released. Each release adds supply, and "
        "existing holders own a smaller share of the total afterwards.",
        "CoinGecko",
    )


def _low_float(info):
    circulating = info.get("circulating_supply")
    total = info.get("max_supply") or info.get("total_supply")
    ratio = _ratio(circulating, total)
    status = NO_DATA if ratio is None else (FLAGGED if ratio < 0.5 else CLEAR)
    return _check(
        "low_float",
        "Most supply not yet circulating",
        status,
        "N/A" if ratio is None else f"{ratio * 100:,.1f}% of supply circulating",
        "Less than 50% of supply circulating",
        "Float: circulating supply divided by maximum (or total) supply.",
        "A low float means the price today is set by a small part of the supply. The rest is held "
        "by teams, investors or treasuries and can reach the market later.",
        "CoinGecko",
    )


# Topics the checks cannot measure from a free, reliable source. They are listed
# in every report under "Not covered" instead of being counted as "No data", which
# would read as a source failing when no source was ever connected.
NOT_COVERED = (
    {
        "name": "Token unlocks in the next 30 days",
        "why": "Dates on which locked tokens become free to trade. Large unlocks often add selling "
               "pressure around the unlock date.",
        "where": "The project's own vesting documents, or a token-unlock tracker such as Tokenomist.",
    },
    {
        "name": "Supply held by a few wallets",
        "why": "When a few wallets hold most of the supply, one decision by one holder can move the price.",
        "where": "A block explorer's top-holders list. Remember that exchange and contract wallets hold "
                 "coins for many people.",
    },
)


def _listing(summary):
    listing = summary.get("listing_status") or {}
    coingecko, cmc = listing.get("listed_on_coingecko"), listing.get("listed_on_coinmarketcap")
    if coingecko is None and cmc is None:
        status, value = NO_DATA, "N/A"
    elif coingecko or cmc:
        names = [n for n, ok in (("CoinGecko", coingecko), ("CoinMarketCap", cmc)) if ok]
        status, value = CLEAR, "Listed on " + " and ".join(names)
    else:
        status, value = FLAGGED, "Not found on CoinGecko or CoinMarketCap"
    return _check(
        "listing_coverage",
        "Not tracked by major data sites",
        status,
        value,
        "Absent from both CoinGecko and CoinMarketCap",
        "Coverage: whether independent market-data sites track the token.",
        "Untracked tokens have less independent price and supply data, and scams are more common "
        "among them. A listing is not an endorsement either.",
        "CoinGecko, CoinMarketCap",
    )


def _drawdown(info):
    change = to_float(info.get("ath_change_pct"))
    status = NO_DATA if change is None else (FLAGGED if change <= -70 else CLEAR)
    return _check(
        "drawdown",
        "Large fall from all-time high",
        status,
        "N/A" if change is None else f"{pct(change, 1)} from all-time high of {usd(info.get('ath_usd'))}",
        "Price more than 70% below its all-time high",
        "Drawdown: how far the price sits below its highest recorded price.",
        "A deep drawdown shows how volatile the token has been. It does not show whether the price "
        "will recover; many tokens never return to an earlier high.",
        "CoinGecko",
    )


def _volatility(info):
    change = to_float(info.get("30d_change_pct"))
    status = NO_DATA if change is None else (FLAGGED if abs(change) > 30 else CLEAR)
    return _check(
        "volatility",
        "Large price swing in 30 days",
        status,
        "N/A" if change is None else f"{pct(change, 1)} over 30 days",
        "Price moved more than 30% up or down in 30 days",
        "Volatility: how much the price has moved over a recent period.",
        "Large swings in either direction mean the value of any holding can change quickly.",
        "CoinGecko",
    )


def _leverage(summary, info):
    derivatives = summary.get("derivatives_data") or {}
    ratio = _ratio(derivatives.get("open_interest"), info.get("market_cap_usd"))
    value = "N/A" if ratio is None else f"Open interest is {ratio * 100:,.1f}% of market cap"
    if derivatives.get("venues") == {} and not derivatives.get("failed"):
        # Every venue answered and none lists a contract: there is no leveraged market to measure
        ratio, value = 0.0, "No perpetual futures market at the venues checked"
    status = NO_DATA if ratio is None else (FLAGGED if ratio > 0.10 else CLEAR)
    return _check(
        "leverage",
        "Heavy leveraged trading",
        status,
        value,
        "Open interest above 10% of market cap",
        "Open interest: the value of futures contracts not yet closed, added up across the venues "
        "named in the source. Venues not named are not counted, so the true total is higher.",
        "Heavy leverage can turn a small price move into a large one, because forced closures "
        "(liquidations) trigger more buying or selling.",
        derivatives.get("source") or "Coinglass",
    )


def compute_risk_checks(data_summary):
    """Run every check against the data summary from the free stage.
    Returns a list of check dicts in a fixed order."""
    info = data_summary.get("token_info") or {}
    return [
        _artificial_volume(info),
        _thin_liquidity(data_summary, info),
        _dilution(info),
        _low_float(info),
        _listing(data_summary),
        _drawdown(info),
        _volatility(info),
        _leverage(data_summary, info),
    ]


def summarise_checks(checks):
    """Count checks by status. Counts, not a score: they are never combined."""
    counts = {FLAGGED: 0, CLEAR: 0, NO_DATA: 0}
    for check in checks:
        counts[check["status"]] += 1
    return counts


def risk_checks_markdown(checks):
    """Render the checks as the report's Risk Checks section."""
    counts = summarise_checks(checks)
    lines = [
        "## Risk Checks",
        "",
        "> **How to read the risk checks:** each check compares one piece of public data with a "
        "teaching threshold chosen by this platform. \"Flagged\" means the data crossed the "
        "threshold. \"Clear\" means it did not. \"No data\" means the platform could not measure "
        "it, which is not the same as clear. The checks are not added up into a score, and none "
        "of them says whether to buy, sell or hold.",
        "",
        f"**{counts[FLAGGED]} flagged, {counts[CLEAR]} clear, {counts[NO_DATA]} with no data.**",
        "",
        "| Check | Result | Measured | Teaching threshold | What it means |",
        "|---|---|---|---|---|",
    ]
    for check in checks:
        lines.append(
            f"| {check['name']} | {STATUS_LABELS[check['status']]} | {check['value']} | "
            f"{check['threshold']} | {check['meaning']} |"
        )
    lines += [
        "",
        "### Not covered by these checks",
        "",
        "No free, reliable source answers these, so the platform does not measure them. Check them yourself:",
        "",
    ]
    lines += [f"- **{item['name']}.** {item['why']} Where to look: {item['where']}" for item in NOT_COVERED]
    lines.append("")
    return "\n".join(lines)
