"""
Main pipeline orchestrator.
Fetches raw data → computes metrics → polls AI models → saves the best report.
"""
import os
import time
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
from data_science.ai_generator import generate_ai_report, extract_final_verdict, extract_blueprint_score

load_dotenv()


def generate_report(token, log_fn=None):
    """
    Fetch raw data → compute metrics → poll AI models → save the best report.

    log_fn: optional callable(str) for live progress updates (e.g. Streamlit status.write).
    Returns the path of the saved report markdown file.
    """
    def log(msg):
        if log_fn:
            log_fn(msg)
        else:
            print(msg)

    token = token.upper()
    log(f"Starting forensic pipeline for **{token}**...")

    # ---- 1. Data Engineering (Extract) ----

    log("Fetching on-chain data from DexScreener...")
    dex_data = fetch_dexscreener_data(token)

    log("Fetching market data, supply, and community stats from CoinGecko...")
    coingecko_data = fetch_coingecko_data(token)

    log("Fetching recent news headlines from CryptoPanic...")
    news_headlines = fetch_cryptopanic_news(token)

    is_cmc_listed = check_cmc_listed(token)

    # Chart screenshot — non-blocking if it fails
    screenshot_path = None
    if "url" in dex_data:
        log("Capturing DexScreener chart screenshot...")
        screenshot_path = capture_dexscreener_chart(token, dex_data["url"])

    log("Fetching derivatives data from Coinglass...")
    coinglass_data = fetch_coinglass_data(token)
    liquidation_data = fetch_liquidation_data(token)

    log("Fetching TVL and protocol data from DefiLlama...")
    defillama_data = fetch_defillama_data(token)

    # ETH-specific burn data
    ultrasound_data = fetch_ultrasound_data(token) if token == "ETH" else {}

    # ---- 2. Data Analytics (Transform) ----

    log("Computing liquidity metrics and kill-switch flags...")
    metrics = compute_derived_metrics(dex_data, token)
    kill_switches = compute_kill_switch_flags(metrics)

    # ---- Build data payload ----

    # Prefer CoinGecko price/market cap over DexScreener when available (more reliable for CEX tokens)
    cg_price = coingecko_data.get("price_usd") if "error" not in coingecko_data else None
    cg_mcap = coingecko_data.get("market_cap_usd") if "error" not in coingecko_data else None

    data_summary = {
        "source_of_truth": "DexScreener (on-chain liquidity) + CoinGecko (market/community) + CryptoPanic (news)",
        "token_info": {
            "name": coingecko_data.get("name") or dex_data.get("name"),
            "symbol": token,
            "chain": dex_data.get("chain"),
            "dex": dex_data.get("dex"),
            "pair_address": dex_data.get("pair_address"),
            "current_price_usd": cg_price or dex_data.get("price_usd"),
            "market_cap_usd": cg_mcap or metrics["market_cap"],
            "fully_diluted_valuation_usd": coingecko_data.get("fully_diluted_valuation_usd"),
            "24h_volume_usd": metrics["volume_24h"],
            "24h_price_change_pct": coingecko_data.get("24h_change_pct"),
            "7d_price_change_pct": coingecko_data.get("7d_change_pct"),
            "30d_price_change_pct": coingecko_data.get("30d_change_pct"),
            "ath_usd": coingecko_data.get("ath_usd"),
            "ath_change_pct": coingecko_data.get("ath_change_pct"),
            "total_supply": coingecko_data.get("total_supply"),
            "circulating_supply": coingecko_data.get("circulating_supply"),
            "max_supply": coingecko_data.get("max_supply"),
            "liquidity_usd": metrics["liquidity_usd"],
            "liquidity_base_tokens": metrics["liquidity_base"],
            "liquidity_quote_tokens": metrics["liquidity_quote"],
            "liquidity_turnover_ratio": metrics["liquidity_turnover_ratio"],
        },
        "community_and_social": {
            "twitter_followers": coingecko_data.get("twitter_followers"),
            "reddit_subscribers": coingecko_data.get("reddit_subscribers"),
            "official_social_links": dex_data.get("social_links", []),
            "official_website_links": dex_data.get("website_links", []),
            "token_categories": coingecko_data.get("categories", []),
            "token_description": coingecko_data.get("description", ""),
        },
        "recent_news_headlines": news_headlines,
        "listing_status": {
            "listed_on_coinmarketcap": is_cmc_listed,
            "listed_on_coingecko": "error" not in coingecko_data,
        },
        "protocol_analytics": defillama_data,
        "eth_burn_data": ultrasound_data,
        "derivatives_data": coinglass_data,
        "liquidation_data": liquidation_data,
    }

    # ---- 3. Data Science (Synthesis) ----

    models_to_run = [
        "google/gemini-2.5-flash",
        "groq/llama-4-maverick",
        "groq/qwen3-32b",
    ]

    best_report_text = None
    best_score = -1
    best_model_name = "Unknown"
    model_results = []
    errors = []

    for model_name in models_to_run:
        log(f"Polling **{model_name}**...")
        for attempt in range(2):
            try:
                current_report = generate_ai_report(token, data_summary, kill_switches, model=model_name)
                current_score = int(extract_blueprint_score(current_report))
                current_verdict = extract_final_verdict(current_report)
                log(f"{model_name} → Blueprint Score {current_score}/100 ({current_verdict})")

                model_results.append({"name": model_name, "score": current_score, "verdict": current_verdict})

                if current_score >= best_score:
                    best_score = current_score
                    best_report_text = current_report
                    best_model_name = model_name
                break

            except Exception as e:
                err_str = str(e)
                if "429" in err_str and attempt == 0:
                    log(f"{model_name} hit rate limit. Retrying in 5s...")
                    time.sleep(5)
                else:
                    log(f"{model_name} failed: {err_str[:120]}")
                    errors.append(f"{model_name}: {err_str}")
                    model_results.append({"name": model_name, "score": -1, "verdict": "Failed"})
                    break

    if not best_report_text:
        raise Exception(f"All 3 AI models failed. {' | '.join(errors)}")

    log(f"Best report: **{best_model_name}** with score {best_score}/100. Saving...")

    # ---- 4. Format and save ----

    verdict = extract_final_verdict(best_report_text)
    score = extract_blueprint_score(best_report_text)

    comparison_md = "\n\n---\n\n## AI Model Comparison\n"
    comparison_md += f"**Winning Model**: {best_model_name} (Blueprint Score: {best_score}/100)\n\n"
    comparison_md += "| Model | Blueprint Score | Verdict | Status |\n|---|---|---|---|\n"
    for m in model_results:
        status_text = "Winner" if m["name"] == best_model_name else "Failed" if m["score"] == -1 else "Runner-up"
        score_text = f"**{m['score']}/100**" if m["score"] != -1 else "N/A"
        comparison_md += f"| **{m['name']}** | {score_text} | **{m['verdict']}** | {status_text} |\n"

    final_markdown = (
        f"---\nToken: {token}\nScore: {score}\nVerdict: {verdict}\nScreenshot: {screenshot_path}\n---\n\n"
        + best_report_text
        + comparison_md
    )

    root_dir = os.path.dirname(os.path.dirname(__file__))
    reports_dir = os.path.join(root_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"{token}_audit_report.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_markdown)

    log(f"Report saved to `{report_path}`")
    return report_path
