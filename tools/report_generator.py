"""
Main pipeline orchestrator.
Fetches raw data -> computes metrics -> calls Anthropic -> saves report.
"""
import os
from dotenv import load_dotenv

from data_engineering.fetchers import (
    fetch_dexscreener_data,
    fetch_coingecko_data,
    fetch_cryptopanic_news,
    fetch_coinglass_data,
    fetch_liquidation_data,
    fetch_defillama_data,
    fetch_ultrasound_data,
    check_cmc_listed,
)
from data_engineering.screenshot_bot import capture_dexscreener_chart
from data_analytics.metrics import compute_derived_metrics, compute_kill_switch_flags
from data_science.ai_generator import generate_ai_report, extract_final_verdict, extract_blueprint_score, infer_verdict_from_score
import db

load_dotenv()

# Maps common full names and aliases to their canonical ticker symbol.
# Prevents duplicate reports like SOLANA vs SOL, ETHEREUM vs ETH.
_TOKEN_ALIASES = {
    "SOLANA": "SOL",
    "ETHEREUM": "ETH",
    "BITCOIN": "BTC",
    "BINANCE": "BNB",
    "POLYGON": "POL",
    "MATIC": "POL",
    "CARDANO": "ADA",
    "AVALANCHE": "AVAX",
    "POLKADOT": "DOT",
    "CHAINLINK": "LINK",
    "ARBITRUM": "ARB",
    "OPTIMISM": "OP",
    "UNISWAP": "UNI",
    "AAVE": "AAVE",
    "COSMOS": "ATOM",
    "NEAR": "NEAR",
    "APTOS": "APT",
    "SUI": "SUI",
}


def normalise_token(token: str) -> str:
    """Resolve full names and known aliases to the canonical ticker symbol."""
    upper = token.strip().upper()
    return _TOKEN_ALIASES.get(upper, upper)


def fetch_and_analyse(token, log_fn=None):
    """
    Free stage: data engineering + analytics only. No AI call, no file write,
    no DB write. Safe to run before any payment is taken.

    log_fn: optional callable(str) for live progress updates in Streamlit.
    Returns {"data_summary": dict, "kill_switches": dict, "screenshot_path": str|None}.
    """
    def log(msg):
        if log_fn:
            log_fn(msg)
        else:
            print(msg)

    token = normalise_token(token)
    log(f"Starting forensic pipeline for **{token}**...")

    # ---- 1. Data Engineering ----

    log("Fetching on-chain data from DexScreener...")
    dex_data = fetch_dexscreener_data(token)

    log("Fetching market data, supply, and community stats from CoinGecko...")
    coingecko_data = fetch_coingecko_data(token)

    log("Fetching recent news headlines...")
    news_headlines = fetch_cryptopanic_news(token)

    is_cmc_listed = check_cmc_listed(token)

    screenshot_path = None
    if "url" in dex_data:
        log("Capturing DexScreener chart screenshot...")
        screenshot_path = capture_dexscreener_chart(token, dex_data["url"])

    log("Fetching derivatives data from Coinglass...")
    coinglass_data = fetch_coinglass_data(token)
    liquidation_data = fetch_liquidation_data(token)

    log("Fetching TVL and protocol data from DefiLlama...")
    defillama_data = fetch_defillama_data(token)

    ultrasound_data = fetch_ultrasound_data(token) if token == "ETH" else {}

    # ---- 2. Analytics ----

    log("Computing liquidity metrics and kill-switch flags...")
    metrics = compute_derived_metrics(dex_data, token)
    kill_switches = compute_kill_switch_flags(metrics)

    # Prefer CoinGecko price/mcap when available
    cg_ok = "error" not in coingecko_data
    data_summary = {
        "source_of_truth": "DexScreener (on-chain) + CoinGecko (market/community) + Google News RSS (news)",
        "token_info": {
            "name": coingecko_data.get("name") if cg_ok else dex_data.get("name"),
            "symbol": token,
            "chain": dex_data.get("chain"),
            "dex": dex_data.get("dex"),
            "pair_address": dex_data.get("pair_address"),
            "current_price_usd": coingecko_data.get("price_usd") if cg_ok else dex_data.get("price_usd"),
            "market_cap_usd": coingecko_data.get("market_cap_usd") if cg_ok else metrics["market_cap"],
            "fully_diluted_valuation_usd": coingecko_data.get("fully_diluted_valuation_usd") if cg_ok else None,
            "24h_change_pct": coingecko_data.get("24h_change_pct") if cg_ok else None,
            "7d_change_pct": coingecko_data.get("7d_change_pct") if cg_ok else None,
            "30d_change_pct": coingecko_data.get("30d_change_pct") if cg_ok else None,
            "ath_usd": coingecko_data.get("ath_usd") if cg_ok else None,
            "ath_change_pct": coingecko_data.get("ath_change_pct") if cg_ok else None,
            "total_supply": coingecko_data.get("total_supply") if cg_ok else None,
            "circulating_supply": coingecko_data.get("circulating_supply") if cg_ok else None,
            "max_supply": coingecko_data.get("max_supply") if cg_ok else None,
            "24h_volume_dex_pair_usd": metrics["volume_24h"],
            "24h_volume_total_all_exchanges_usd": coingecko_data.get("total_volume_24h_usd") if cg_ok else None,
            "liquidity_usd": metrics["liquidity_usd"],
            "liquidity_base_tokens": metrics["liquidity_base"],
            "liquidity_quote_tokens": metrics["liquidity_quote"],
            "liquidity_turnover_ratio": metrics["liquidity_turnover_ratio"],
        },
        "community_and_social": {
            # Follower counts: CoinGecko removed these from free tier; Reddit needs OAuth keys in .env
            "twitter_followers": coingecko_data.get("twitter_followers") if cg_ok else None,
            "twitter_screen_name": coingecko_data.get("twitter_screen_name", "") if cg_ok else "",
            "reddit_subscribers": coingecko_data.get("reddit_subscribers") if cg_ok else None,
            "reddit_active_users": coingecko_data.get("reddit_active_users") if cg_ok else None,
            "subreddit": coingecko_data.get("subreddit_name", "") if cg_ok else "",
            # Note for AI: handles are available even when counts are not
            "social_note": (
                f"Twitter handle: @{coingecko_data.get('twitter_screen_name', 'unavailable')} | "
                f"Subreddit: r/{coingecko_data.get('subreddit_name', 'unavailable')} | "
                "Follower counts require paid API access; use news headlines for sentiment assessment."
            ) if cg_ok else "Social data unavailable",
            "official_social_links": dex_data.get("social_links", []),
            "official_website_links": dex_data.get("website_links", []),
            "token_categories": coingecko_data.get("categories", []) if cg_ok else [],
            "token_description": coingecko_data.get("description", "") if cg_ok else "",
        },
        "recent_news_headlines": news_headlines,
        "listing_status": {
            "listed_on_coinmarketcap": is_cmc_listed,
            "listed_on_coingecko": cg_ok,
        },
        "protocol_analytics": defillama_data,
        "eth_burn_data": ultrasound_data,
        "derivatives_data": coinglass_data,
        "liquidation_data": liquidation_data,
    }

    return {
        "data_summary": data_summary,
        "kill_switches": kill_switches,
        "screenshot_path": screenshot_path,
    }


def generate_ai_and_save(token, data_summary, kill_switches, screenshot_path, model="claude-sonnet-4-6", log_fn=None, payment_id=None):
    """
    Paid stage: the Anthropic call, score/verdict extraction, markdown assembly,
    local file write, and the authoritative DB row. Only call this once a report
    has actually been paid for (or, for local-dev scripts, with payment_id=None).

    model:      Anthropic model ID. Default is claude-sonnet-4-6.
                Pass "claude-opus-4-8" for maximum analytical depth.
    log_fn:     optional callable(str) for live progress updates in Streamlit.
    payment_id: the payments.id row this report was unlocked by, or None for
                unpaywalled local-dev calls.
    Returns the path of the saved local report file.
    """
    def log(msg):
        if log_fn:
            log_fn(msg)
        else:
            print(msg)

    token = normalise_token(token)

    # ---- 3. AI Report Generation ----

    log(f"Generating report with **{model}**...")
    report_text = generate_ai_report(token, data_summary, kill_switches, model=model)

    score = extract_blueprint_score(report_text)
    verdict = extract_final_verdict(report_text)
    # Fall back to score-derived verdict if the AI did not write a readable Final Verdict
    if verdict == "Unknown" and score > 0:
        verdict = infer_verdict_from_score(score)
    log(f"Report complete. Blueprint Score: {score}/100 | Verdict: {verdict}")

    # ---- 4. Save ----

    final_markdown = (
        f"---\nToken: {token}\nScore: {score}\nVerdict: {verdict}\n"
        f"Model: {model}\nScreenshot: {screenshot_path}\n---\n\n"
        + report_text
    )

    root_dir = os.path.dirname(os.path.dirname(__file__))
    reports_dir = os.path.join(root_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"{token}_audit_report.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_markdown)

    log(f"Saved to `{report_path}`")

    db.save_report(
        token_symbol=token,
        payment_id=payment_id,
        model=model,
        score=score,
        verdict=verdict,
        screenshot_path=screenshot_path,
        markdown=final_markdown,
    )

    return report_path


def generate_report(token, model="claude-sonnet-4-6", log_fn=None):
    """
    Thin wrapper: fetch_and_analyse() + generate_ai_and_save() in sequence, unpaywalled.
    Unchanged signature and behaviour for existing local-dev callers
    (dashboards/app.py's legacy path, debug_btc.py, test_adr.py, test_run.py).

    model:  Anthropic model ID. Default is claude-sonnet-4-6.
            Pass "claude-opus-4-8" for maximum analytical depth.
    log_fn: optional callable(str) for live progress updates in Streamlit.
    Returns the path of the saved report file.
    """
    result = fetch_and_analyse(token, log_fn=log_fn)
    return generate_ai_and_save(
        token,
        result["data_summary"],
        result["kill_switches"],
        result["screenshot_path"],
        model=model,
        log_fn=log_fn,
    )
