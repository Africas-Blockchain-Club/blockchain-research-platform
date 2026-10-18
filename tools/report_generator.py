"""
Main pipeline orchestrator.

Stage 1 (free, no AI): fetch public data, compute metrics, run the risk checks.
Stage 2, one of:
  - the data-only report, built by code (always available; the AI off state)
  - the AI write-up, which must pass the structure check and the advice check
    before it is saved; on any failure nothing is saved and the error says why

Run from the command line:
  python -m tools.report_generator SOL              # AI write-up if AI is on
  python -m tools.report_generator SOL --data-only  # no AI, no cost
"""
import argparse
import datetime
import logging

from config import SETTINGS
from data_analytics.chains import CHAIN_ALIASES, profile
from data_analytics.data_report import build_data_report, quoted_passages
from data_analytics.metrics import compute_derived_metrics
from data_analytics.risk_profile import compute_risk_checks
from data_engineering.fetchers import (
    check_cmc_listed,
    fetch_coingecko_data,
    fetch_coinglass_data,
    fetch_cryptopanic_news,
    fetch_defillama_data,
    fetch_dexscreener_data,
    fetch_liquidation_data,
    fetch_ultrasound_data,
    fetch_usd_zar,
    token_contracts,
)
from data_engineering.github_activity import fetch_github_activity
from data_engineering.networks import fetch_network
from data_engineering.screenshot_bot import capture_dexscreener_chart
from data_science.ai_generator import generate_ai_report, validate_structure
from data_science.compliance import assert_educational
from data_science.llm import AIResponseError
from tools import report_store

log = logging.getLogger(__name__)

# Maps common full names and aliases to their canonical ticker symbol, so the
# same token is never stored twice (SOLANA and SOL).
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
    "COSMOS": "ATOM",
    "APTOS": "APT",
}


def normalise_token(token):
    """Resolve chain names, full names and known aliases to the native asset's
    ticker symbol, so "Bitcoin", "solana" and "XRP Ledger" all work."""
    upper = " ".join(token.strip().upper().split())
    return CHAIN_ALIASES.get(upper) or _TOKEN_ALIASES.get(upper, upper)


def _listed_on_coingecko(coingecko_data):
    """True, False, or None when CoinGecko could not be asked. A rate limit
    or outage must not read as "not listed"."""
    if "error" not in coingecko_data:
        return True
    return False if "not found" in coingecko_data["error"].lower() else None


def fetch_and_analyse(token, log_fn=None):
    """Stage 1: data and rule-based analysis only. No AI call, no file write.

    log_fn: optional callable(str) for live progress messages.
    Returns {"token", "data_summary", "risk_checks", "screenshot_path"}.
    """
    say = log_fn or log.info
    token = normalise_token(token)

    say("Reading market, supply and project data from CoinGecko...")
    coingecko_data = fetch_coingecko_data(token)
    say("Finding the token's main exchange pool on DexScreener...")
    dex_data = fetch_dexscreener_data(
        token,
        contracts=token_contracts(token, coingecko_data.get("platforms")),
        reference_price=coingecko_data.get("price_usd"),
    )
    say("Reading recent headlines...")
    news_headlines = fetch_cryptopanic_news(token)
    is_cmc_listed = check_cmc_listed(token)

    screenshot_path = None
    if "url" in dex_data and SETTINGS.screenshots_enabled:
        say("Capturing the DexScreener chart...")
        screenshot_path = capture_dexscreener_chart(token, dex_data["url"])

    say("Reading derivatives data from Coinglass...")
    coinglass_data = fetch_coinglass_data(token)
    liquidation_data = fetch_liquidation_data(token)
    say("Reading protocol data from DefiLlama...")
    defillama_data = fetch_defillama_data(token, name=coingecko_data.get("name"))
    ultrasound_data = fetch_ultrasound_data(token) if token == "ETH" else {}

    say("Reading the blockchain's live network data...")
    network = fetch_network(token)

    rate, rate_source = fetch_usd_zar()
    if rate is None:
        say(f"Live exchange rate unavailable ({rate_source}); using the configured rate of {SETTINGS.fallback_usd_zar} ZAR per USD.")
        rate, rate_source = SETTINGS.fallback_usd_zar, "configured fallback rate (FALLBACK_USD_ZAR)"

    metrics = compute_derived_metrics(dex_data, token)
    cg_ok = "error" not in coingecko_data
    cg = coingecko_data if cg_ok else {}
    data_summary = {
        "source_of_truth": "Blockchain profile (hand-checked) + public network endpoints + CoinGecko (market, project, developer activity) + DexScreener (on-chain pool) + DefiLlama + Google News RSS",
        "fx": {"usd_zar": rate, "source": rate_source},
        # The chain first: its hand-checked profile (featured chains) and live network data
        "blockchain": {"profile": profile(token), "network": network},
        "developer_activity": fetch_github_activity((profile(token) or {}).get("repo")),
        "token_info": {
            "name": cg.get("name") or dex_data.get("name"),
            "symbol": token,
            "chain": dex_data.get("chain"),
            "dex": dex_data.get("dex"),
            "dex_pair_match": dex_data.get("match") or dex_data.get("error"),
            "pair_address": dex_data.get("pair_address"),
            "current_price_usd": cg.get("price_usd") or dex_data.get("price_usd"),
            "market_cap_usd": cg.get("market_cap_usd") or metrics["market_cap"] or None,
            "fully_diluted_valuation_usd": cg.get("fully_diluted_valuation_usd"),
            "24h_change_pct": cg.get("24h_change_pct"),
            "7d_change_pct": cg.get("7d_change_pct"),
            "30d_change_pct": cg.get("30d_change_pct"),
            "ath_usd": cg.get("ath_usd"),
            "ath_change_pct": cg.get("ath_change_pct"),
            "total_supply": cg.get("total_supply"),
            "circulating_supply": cg.get("circulating_supply"),
            "max_supply": cg.get("max_supply"),
            "24h_volume_dex_pair_usd": metrics["volume_24h"],
            "24h_volume_total_all_exchanges_usd": cg.get("total_volume_24h_usd"),
            "liquidity_usd": metrics["liquidity_usd"],
            "liquidity_base_tokens": metrics["liquidity_base"],
            "liquidity_quote_tokens": metrics["liquidity_quote"],
            "liquidity_turnover_ratio_pct": metrics["liquidity_turnover_ratio"],
            "depth_to_mcap_ratio_pct": metrics["depth_to_mcap_ratio"],
        },
        "community_and_social": {
            "twitter_screen_name": cg.get("twitter_screen_name", ""),
            "subreddit": cg.get("subreddit_name", ""),
            "official_social_links": dex_data.get("social_links", []),
            "official_website_links": dex_data.get("website_links", []),
            "token_categories": cg.get("categories", []),
            "token_description": cg.get("description", ""),
        },
        "recent_news_headlines": news_headlines,
        "listing_status": {
            "listed_on_coinmarketcap": is_cmc_listed,
            "listed_on_coingecko": _listed_on_coingecko(coingecko_data),
        },
        "source_errors": {
            name: data["error"]
            for name, data in (("dexscreener", dex_data), ("coingecko", coingecko_data))
            if isinstance(data, dict) and "error" in data
        },
        "protocol_analytics": defillama_data,
        "eth_burn_data": ultrasound_data,
        "derivatives_data": coinglass_data,
        "liquidation_data": liquidation_data,
    }

    if "error" in dex_data and not cg_ok:
        raise LookupError(
            f"No data found for {token}: DexScreener said \"{dex_data['error']}\" and CoinGecko said "
            f"\"{coingecko_data['error']}\". Check the ticker and try again."
        )

    say("Running the risk checks...")
    return {
        "token": token,
        "data_summary": data_summary,
        "risk_checks": compute_risk_checks(data_summary),
        "screenshot_path": screenshot_path,
    }


def _today():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%d %B %Y")


def save_data_report(analysis, payment_id=None):
    """Stage 2, AI off: build and save the data-only report. Returns metadata."""
    token = analysis["token"]
    body = build_data_report(token, analysis["data_summary"], _today())
    # The template is code we control, but checking it too keeps the rule universal
    assert_educational(body, quoted=quoted_passages(analysis["data_summary"]))
    return report_store.save_report(
        token,
        body,
        mode=report_store.MODE_DATA,
        model=None,
        risk_checks=analysis["risk_checks"],
        data_summary=analysis["data_summary"],
        screenshot_path=analysis["screenshot_path"],
        payment_id=payment_id,
    )


def save_ai_report(analysis, model=None, payment_id=None, log_fn=None):
    """Stage 2, AI on: write, check and save the AI report. Returns metadata.

    Raises llm.AIUnavailableError / AIRefusalError / AIResponseError, or
    compliance.AdviceLanguageError. Nothing is saved when any of them is raised.
    """
    say = log_fn or log.info
    token = analysis["token"]
    model = model or SETTINGS.default_model
    say(f"Writing the report with {model}. This can take a few minutes...")
    result = generate_ai_report(token, analysis["data_summary"], analysis["risk_checks"], _today(), model=model)

    missing = validate_structure(result["text"])
    if missing:
        raise AIResponseError(
            f"The AI write-up is missing required sections ({', '.join(missing)}), so it was not saved. Try again."
        )
    say("Checking the write-up for advice language...")
    assert_educational(result["text"], quoted=quoted_passages(analysis["data_summary"]))

    return report_store.save_report(
        token,
        result["text"],
        mode=report_store.MODE_AI,
        model=result["model"],
        risk_checks=analysis["risk_checks"],
        data_summary=analysis["data_summary"],
        screenshot_path=analysis["screenshot_path"],
        payment_id=payment_id,
        cost_usd=result["cost_usd"],
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate an educational token research report.")
    parser.add_argument("token", help="Ticker or name, for example SOL or solana")
    parser.add_argument("--data-only", action="store_true", help="Skip the AI write-up (no API key needed)")
    parser.add_argument("--model", default=None, help=f"AI model (default {SETTINGS.default_model})")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    analysis = fetch_and_analyse(args.token)
    if args.data_only or not SETTINGS.ai_enabled:
        if not args.data_only:
            log.warning("%s Writing the data-only report instead.", SETTINGS.ai_off_reason)
        meta = save_data_report(analysis)
    else:
        meta = save_ai_report(analysis, model=args.model)
    log.info("Saved %s report for %s: %s flagged, %s clear, %s no data.",
             meta["mode"], meta["token"], meta["flagged"], meta["clear"], meta["no_data"])


if __name__ == "__main__":
    main()
