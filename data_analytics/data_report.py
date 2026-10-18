"""
The data-only report: the platform's defined off state for AI.

Built entirely by code from the free-stage data, so it costs nothing, runs
with no API key, and contains no model-written text. It follows the same
phase headings as the AI write-up so the dashboard reads both the same way.
The AI write-up adds explanation; this report is the floor that is always
available.
"""
from data_analytics.formatting import count, pct, to_float, usd, usd_zar

STRESS_SIZES_USD = (50_000, 100_000, 500_000, 1_000_000, 5_000_000)


def sell_price_impact(pool_base_tokens, price_usd, sale_usd):
    """Price fall caused by selling sale_usd of the token into a constant
    product pool (x * y = k), ignoring fees. Returns a fraction (0.05 = 5%).

    Selling dx tokens takes the pool from x to x + dx. With k fixed, the price
    (y / x) moves by the factor (x / (x + dx)) squared, so the result does not
    depend on what the quote token is."""
    base, price = to_float(pool_base_tokens), to_float(price_usd)
    if not base or not price or base <= 0 or price <= 0:
        return None
    sold = sale_usd / price
    return 1 - (base / (base + sold)) ** 2


def _table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def _clean(text, limit=None):
    text = " ".join(str(text or "").replace("|", "/").split())
    if limit and len(text) > limit:
        text = text[: limit - 3].rsplit(" ", 1)[0] + "..."
    return text or "N/A"


def build_data_report(token, data_summary, date_str):
    info = data_summary.get("token_info") or {}
    social = data_summary.get("community_and_social") or {}
    rate = (data_summary.get("fx") or {}).get("usd_zar") or 0
    money = lambda v: usd_zar(v, rate)  # noqa: E731 - local shorthand keeps the tables readable

    parts = [f"# {token} Research Report - {date_str}", ""]

    parts += [
        "## How to Read This Report",
        "",
        "> This is the data-only version of the report: every number comes straight from the "
        "sources listed at the end, and no AI wrote any of it. Phase 0 sets out what the token is. "
        "Phase 1 looks at supply: how many tokens exist and how many are trading. Phase 1.5 and "
        "Phase 2 show how the main exchange pool prices the token and what a large sale would do "
        "to that price. Phase 3 covers leveraged trading. The risk checks then compare the data "
        "against teaching thresholds. A check that says \"No data\" means the platform could not "
        "measure it, not that the risk is absent.",
        "",
    ]

    description = _clean(social.get("token_description"), 700)
    parts += [
        "## Phase 0: Overview and Narrative",
        "",
        "### 0.1 Token Snapshot",
        "",
        "**Identity**",
        "",
        _table(
            ["Name", "Symbol", "Chain", "Main DEX", "Categories"],
            [[_clean(info.get("name")), token, _clean(info.get("chain")), _clean(info.get("dex")),
              _clean(", ".join((social.get("token_categories") or [])[:4]))]],
        ),
        "",
        "**Price and Performance**",
        "",
        _table(
            ["Price", "24h Change", "7d Change", "30d Change"],
            [[money(info.get("current_price_usd")), pct(info.get("24h_change_pct")),
              pct(info.get("7d_change_pct")), pct(info.get("30d_change_pct"))]],
        ),
        "",
        "**Market Size**",
        "",
        _table(
            ["Market Cap", "Fully Diluted Value", "All-Time High", "Change From All-Time High"],
            [[money(info.get("market_cap_usd")), money(info.get("fully_diluted_valuation_usd")),
              usd(info.get("ath_usd")), pct(info.get("ath_change_pct"))]],
        ),
        "",
        "> **Reading this table:** market cap is price multiplied by circulating supply. Fully "
        "diluted value uses the maximum supply instead, so the gap between the two shows how many "
        "tokens are still to come.",
        "",
        "### 0.2 What the Project Says About Itself",
        "",
        f"> {description}",
        "",
        "This is the project's own description, as listed on CoinGecko. Treat it as a claim to "
        "check, not as evidence.",
        "",
        "### 0.3 Recent News Headlines",
        "",
    ]

    headlines = [h for h in data_summary.get("recent_news_headlines") or [] if h.get("title")]
    if headlines:
        parts.append(_table(
            ["Headline", "Source", "Published"],
            [[_clean(h["title"], 140), _clean(h.get("source")), _clean(h.get("published_at"))] for h in headlines[:8]],
        ))
        parts += ["", "> **Reading this table:** headlines show what people are talking about, not "
                  "what is true. Open the source and check who is making each claim.", ""]
    else:
        parts += ["No headlines could be fetched.", ""]

    circulating, total, maximum = (info.get("circulating_supply"), info.get("total_supply"), info.get("max_supply"))
    reference = to_float(maximum) or to_float(total)
    share = (to_float(circulating) / reference * 100) if to_float(circulating) and reference else None
    parts += [
        "## Phase 1: Supply",
        "",
        "### 1.1 Supply Overview",
        "",
        _table(
            ["Metric", "Value", "What This Means"],
            [
                ["Circulating Supply", count(circulating), "Tokens trading in the market today"],
                ["Total Supply", count(total), "Tokens created so far, including locked tokens"],
                ["Maximum Supply", count(maximum), "The hard cap, if the project has one"],
                ["Share Circulating", pct(share, 1), "A low share means more supply can still reach the market"],
            ],
        ),
        "",
        "> **Reading this table:** a token with no maximum supply can keep issuing new tokens. "
        "Check the project's documents for its issuance rules and vesting schedule.",
        "",
    ]

    base, quote = to_float(info.get("liquidity_base_tokens")), to_float(info.get("liquidity_quote_tokens"))
    price = info.get("current_price_usd")
    parts += [
        "## Phase 1.5: Exchange Pool Maths",
        "",
        f"Main pool: {_clean(info.get('dex'))} on {_clean(info.get('chain'))}, found by "
        f"{_clean(info.get('dex_pair_match'))}.",
        "",
    ]
    if base and quote:
        k = base * quote
        # Buying 10% of x out leaves 0.9x, so the price rises by (1 / 0.9) squared
        buy_out_rise = (1 / 0.9) ** 2 - 1
        parts += [
            "Most decentralised exchanges price a token with the constant product formula: "
            "x multiplied by y equals k. x is the number of tokens in the pool, y is the number of "
            "the paired token, and k stays fixed. When someone buys tokens out of the pool, x falls, "
            "so y has to rise to keep k the same, and the price goes up. Selling does the opposite.",
            "",
            _table(
                ["Variable", "Value"],
                [
                    ["Tokens in pool (x)", count(base)],
                    ["Paired tokens in pool (y)", count(quote)],
                    ["k = x multiplied by y", f"{k:,.0f}"],
                    ["Price change if 10% of x is bought out", pct(buy_out_rise * 100, 1)],
                ],
            ),
            "",
        ]
    else:
        parts += ["The pool's token balances were not available, so the pool maths cannot be shown.", ""]

    parts += [
        "## Phase 2: Market Structure",
        "",
        "### 2.1 Liquidity",
        "",
        _table(
            ["Metric", "Value", "What This Measures"],
            [
                ["Main DEX pool liquidity", money(info.get("liquidity_usd")), "Money in the main pool backing the price"],
                ["24h volume, main DEX pool", money(info.get("24h_volume_dex_pair_usd")), "Trading in that one pool"],
                ["24h volume, all exchanges", money(info.get("24h_volume_total_all_exchanges_usd")), "Trading everywhere CoinGecko tracks"],
            ],
        ),
        "",
        "### 2.2 What a Large Sale Would Do",
        "",
    ]
    impacts = [(size, sell_price_impact(base, price, size)) for size in STRESS_SIZES_USD]
    if any(impact is not None for _, impact in impacts):
        parts += [
            _table(
                ["Sale Size", "Estimated Price Fall in the Main Pool"],
                [[money(size), pct(impact * 100 if impact is not None else None, 2)] for size, impact in impacts],
            ),
            "",
            "> **Reading this table:** these figures assume the whole sale goes through the main "
            "DEX pool at once, with no fees and no arbitrage traders refilling it. Real trades are "
            "often split across exchanges, and many pools (Uniswap version 3, Orca) concentrate "
            "liquidity near the current price, which changes the real figure. Treat the numbers "
            "as a teaching estimate of pool depth, not a forecast.",
            "",
        ]
    else:
        parts += ["Pool depth or price was not available, so the estimate cannot be shown.", ""]

    defi = data_summary.get("protocol_analytics") or {}
    parts += ["## Phase 2.5: DeFi Mechanics", ""]
    if defi and "error" not in defi and "note" not in defi:
        labels = {"kind": "Tracked as", "name": "Name on DefiLlama", "tvl_usd": "Total value locked (TVL)",
                  "category": "Category", "chains": "Chains", "match": "How it was matched"}
        rows = [[label, money(defi[key]) if key == "tvl_usd" else _clean(defi[key], 120)]
                for key, label in labels.items() if defi.get(key) not in (None, "")]
        parts += [
            _table(["Field", "Value"], rows),
            "",
            "> **Reading this table:** total value locked is the money deposited in a chain's or "
            "protocol's smart contracts. It shows how much the system is used, not what the token is worth.",
            "",
        ]
    else:
        parts += [_clean(defi.get("note") or defi.get("error") or "No protocol data was found on DefiLlama."), ""]

    derivatives = data_summary.get("derivatives_data") or {}
    parts += ["## Phase 3: Derivatives", ""]
    if derivatives and "error" not in derivatives:
        parts += [
            _table(
                ["Metric", "Value"],
                [
                    ["Open interest", money(derivatives.get("open_interest"))],
                    ["24h derivatives volume", money(derivatives.get("vol_usd"))],
                ],
            ),
            "",
            "> **Reading this table:** open interest is the value of futures contracts not yet closed. "
            "When it is large compared with market cap, forced closures can make price moves bigger.",
            "",
        ]
    else:
        parts += [
            "Derivatives data is not connected. It needs a COINGLASS_API_KEY in .env.",
            "",
        ]

    parts += [
        "## Phase 4: Questions to Research Further",
        "",
        "- Who holds the largest share of supply? Check the top holders on a block explorer.",
        "- When do locked tokens unlock? Find the vesting schedule in the project's documents.",
        "- What does the token do? Read the project's documents and check whether the token is needed to use the product.",
        "- Who builds it? Check the public code repository for recent activity.",
        "- What do regulators say? Search for the project's name on the FSCA and SEC websites.",
        "",
    ]
    return "\n".join(parts)
