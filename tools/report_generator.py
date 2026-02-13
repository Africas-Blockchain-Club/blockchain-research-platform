import os
import datetime
import base64
import json
import re
import requests

from pycoingecko import CoinGeckoAPI
import matplotlib.pyplot as plt
from openai import OpenAI
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from dotenv import load_dotenv
from google import genai

load_dotenv()


# ====================== DATA FETCHERS ======================

def fetch_coinglass_data(token, api_key=None):
    """Fetch derivatives data from Coinglass API (requires free API key from open.coinglass.com)"""
    if not api_key:
        return {"error": "COINGLASS_API_KEY not set"}

    headers = {"coinglassSecret": api_key}

    try:
        # Open Interest
        oi_url = f"https://open-api.coinglass.com/public/v2/open_interest?symbol={token.upper()}&time_type=m5"
        oi_response = requests.get(oi_url, headers=headers)
        oi_data = oi_response.json() if oi_response.status_code == 200 else {}

        # Funding Rate
        fr_url = f"https://open-api.coinglass.com/public/v2/funding?symbol={token.upper()}&time_type=m5"
        fr_response = requests.get(fr_url, headers=headers)
        fr_data = fr_response.json() if fr_response.status_code == 200 else {}

        return {
            "open_interest": oi_data.get("data", []),
            "funding_rate": fr_data.get("data", [])
        }
    except Exception as e:
        return {"error": f"Coinglass API error: {str(e)}"}


def fetch_liquidation_data(token, api_key=None):
    """Fetch liquidation data from Coinglass API for heatmap analysis"""
    if not api_key:
        return {"error": "COINGLASS_API_KEY not set"}

    headers = {"coinglassSecret": api_key}

    try:
        url = f"https://open-api.coinglass.com/public/v2/liquidation_info?symbol={token.upper()}&time_type=h4"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "liquidation_levels": data.get("data", []),
                "source": "Coinglass"
            }
        return {"error": f"Coinglass liquidation API returned {response.status_code}"}
    except Exception as e:
        return {"error": f"Coinglass liquidation API error: {str(e)}"}


def fetch_treasuries(token):
    """Fetch treasury data for Bitcoin and Ethereum"""
    if token.lower() not in ['btc', 'eth']:
        return []

    try:
        if token.lower() == 'btc':
            url = "https://api.treasury.gov/v1/debt/top/top_100_holders.json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                btc_entities = [item for item in data if 'bitcoin' in str(item).lower() or 'crypto' in str(item).lower()]
                return btc_entities[:5]
        elif token.lower() == 'eth':
            return [{"entity": "Ethereum Foundation", "holdings": "Unknown", "notes": "No direct treasury tracking"}]
    except Exception as e:
        return [{"error": f"Treasury fetch failed: {str(e)}"}]

    return []


def fetch_ultrasound_data(token):
    """Fetch ultrasound money data for Ethereum"""
    if token.lower() != 'eth':
        return {"error": "Ultrasound data only available for ETH"}

    try:
        url = "https://api.ultrasound.money/v2/fees/1d"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "daily_burn": data.get("daily_burn", 0),
                "daily_issuance": data.get("daily_issuance", 0),
                "net_supply_change": data.get("net_supply_change", 0),
                "timestamp": data.get("timestamp")
            }
    except Exception as e:
        return {"error": f"Ultrasound API error: {str(e)}"}


# ====================== ANALYSIS HELPERS ======================

def compute_kill_switch_flags(data_summary):
    """
    Compute the 4 Kill Switch red-flag checks from available data.
    Returns a dict of flag_name -> {triggered: bool, value: ..., reason: str}
    """
    flags = {}
    market_cap = data_summary.get("token_info", {}).get("market_cap", 0) or 0
    volume_24h = data_summary.get("token_info", {}).get("24h_volume", 0) or 0

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
    liquidity = data_summary.get("liquidity", [])
    if liquidity and market_cap > 100_000_000:
        total_volume = sum(t.get("volume", 0) or 0 for t in liquidity)
        # Rough proxy: if top-5 exchange volume is very low relative to MCap
        flags["thin_order_books"] = {
            "triggered": total_volume < 500_000,
            "value": total_volume,
            "reason": f"Top exchange volume = ${total_volume:,.0f}. For a >${market_cap/1e6:.0f}M MCap token, depth < $500k signals a liquidity trap."
        }
    else:
        flags["thin_order_books"] = {
            "triggered": False,
            "value": None,
            "reason": "Requires ±2% order-book depth data (Coinglass/Kaiko premium). Flagged for AI assessment."
        }

    # 3. Supply Unlock Cliff (>15% unlocking in 30 days)
    circulating = data_summary.get("token_info", {}).get("circulating_supply", 0) or 0
    total = data_summary.get("token_info", {}).get("total_supply", 0) or 0
    if circulating > 0 and total > 0:
        locked_pct = (1 - circulating / total) * 100
        flags["supply_unlock_cliff"] = {
            "triggered": False,  # CoinGecko doesn't provide unlock schedules; AI must assess
            "value": round(locked_pct, 2),
            "reason": f"{locked_pct:.1f}% of total supply is not circulating. Unlock schedule analysis requires TokenUnlocks.app data — flagged for AI assessment."
        }
    else:
        flags["supply_unlock_cliff"] = {"triggered": False, "value": None, "reason": "Supply data unavailable."}

    # 4. Concentration Risk (top 10 wallets >80%)
    flags["concentration_risk"] = {
        "triggered": False,
        "value": None,
        "reason": "Requires on-chain wallet distribution data (Arkham/Nansen). Flagged for AI assessment."
    }

    return flags


def extract_blueprint_score(report_text):
    """Extract the Blueprint Score from the generated report.
    Tries multiple patterns since AI models format the score differently:
    - In a markdown table Total row:  | **Total** | **100** | **75/100** |
    - On the same line as heading:    Blueprint Score: **75/100**
    - Anywhere as X/100:              overall score of 75/100
    """
    score_patterns = [
        # Table Total row:  | **Total** | ... | **75/100** |
        r'\*{0,2}Total\*{0,2}\s*\|[^|]*\|\s*\*{0,2}(\d{1,3})\s*/\s*100\*{0,2}',
        # Same line as heading: Blueprint Score ... 75/100 or **75/100**
        r'Blueprint\s+Score[^\n]*?\*{0,2}(\d{1,3})\s*/\s*100\*{0,2}',
        # Broad fallback: any line with a number /100
        r'(\d{1,3})\s*/\s*100',
    ]
    for pattern in score_patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return score
    return 0


def extract_final_verdict(report_text):
    """Extract the Final Verdict rating from the generated report.
    Handles varied markdown formatting around the rating keyword.
    """
    verdict_options = r'(Strong\s+Buy|Accumulate|Neutral|Distribute|Strong\s+Sell)'
    patterns = [
        # **Rating**: Strong Buy  or  **Rating:** Strong Buy
        r'\*{0,2}Rating\*{0,2}\s*:\s*\*{0,2}' + verdict_options + r'\*{0,2}',
        # Final Verdict ... : Strong Buy
        r'(?:Final\s+)?Verdict[^:]*:\s*\*{0,2}' + verdict_options + r'\*{0,2}',
    ]
    for pattern in patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            return re.sub(r'\s+', ' ', match.group(1).strip())
    return "Unknown"


# ====================== AI PROMPT ======================

SYSTEM_PROMPT = """You are a senior blockchain data scientist producing institutional-grade forensic audit reports.

CRITICAL RULES:
1. Write in British English throughout (e.g., "analyse" not "analyze", "colour" not "color", "behaviour" not "behavior", "defence" not "defense", "realised" not "realized").
2. Do NOT begin the report with any preamble, greeting, or meta-commentary (e.g., never start with "Certainly!", "Below is…", "Here is…"). Begin DIRECTLY with the report title.
3. Use the exact 4-phase structure below. Every section must appear.

REPORT STRUCTURE (follow exactly):

# [TOKEN] Forensic Audit — [DATE]

## Phase 1: The Hard Data (Supply Forensics)
### 1.1 Tokenomics & Supply Dynamics
### 1.2 Sovereign & Institutional Inventory
- Table of "Verified Asset Inventory" classifying entities as Forced Sellers vs Strategic Holders
### 1.3 The "Permanent Scarcity" Layer
- Calculate Effective Supply using: Total Supply − (Dormant coins > 5yr) − (Burn addresses)
- For ETH: reference ultrasound.money burn data if provided
### 1.4 Behavioural Waves (HODL Analysis)
- Assess LTH vs STH behaviour signals (Distribution or Capitulation)

## Phase 2: Market Structure (The Liquidity Layer)
### 2.1 Liquidity & Order Book Depth
- Analyse liquidity metrics: Turnover Ratio, depth, spread, slippage
- Stress Test: simulate $1M, $5M, $10M market sell impact
### 2.2 Liquidity Assessment
- Why liquidity matters for this specific token
### 2.3 Cost Basis Analysis
- Realised Price assessment, STH cost basis signal

## Phase 3: Derivatives & Sentiment (The Volatility Layer)
### 3.1 Institutional & Leverage Cycle Detection
### 3.2 Liquidation Heatmaps
### 3.3 Funding & Open Interest
- OI vs price divergence check
- Funding Rate sentiment check

## Phase 4: The Synthesis & Blueprint Score
### 4.1 The Synthesis Equation
Write ONE narrative sentence:
"[Supply Constraint Status] + [Holder Behaviour] + [Market Structure Integrity] + [Derivatives Positioning] = [Conclusion]"

### 4.2 The Blueprint Score (0–100)
Score each component and show the breakdown:
| Component | Weight | Score | Reasoning |
|---|---|---|---|
| Scarcity / Supply Integrity | 30 | /30 | ... |
| Liquidity / Depth | 30 | /30 | ... |
| On-Chain Sentiment | 20 | /20 | ... |
| Derivative Structure | 20 | /20 | ... |
| **Total** | **100** | **X/100** | |

### 4.3 Final Verdict
- **Rating**: (Strong Buy / Accumulate / Neutral / Distribute)
- **Entry Trigger**: one specific trigger
- **Exit Trigger**: one specific trigger

## Red Flag Kill Switch Assessment
Evaluate each kill switch trigger. If ANY are True, override the Blueprint Score to < 20:
- [ ] Thin Order Books (±2% depth < $500k for >$100M MCap)
- [ ] Supply Influx (>15% unlocking in 30 days)
- [ ] Concentration Risk (top 10 wallets > 80%)
- [ ] Artificial Volume (Volume/MCap > 1.0)

## Source Layer
List all data sources used.

Where data is unavailable, explicitly state "Data Unavailable — Requires [Source]" and provide your best analytical estimate based on available context. Do NOT fabricate data points.

Use markdown tables, bold key numbers, and keep the analysis data-driven. Include chart placeholders where indicated: ![Price Chart](price_chart) and ![Market Cap Chart](market_cap_chart).
"""


# ====================== REPORT GENERATION ======================

def _call_openrouter(system_prompt, user_prompt):
    """Call OpenRouter API and return report text"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    # Primary: Claude 3.5 Sonnet (Premium) - SOTA reasoning/coding
    # Fallback: openrouter/free (Auto-selects best free model)
    models_to_try = [
        os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        "openrouter/free",
    ]

    for model in models_to_try:
        try:
            print(f"    Trying OpenRouter model: {model}...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=6000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"    ⚠️ Failed with {model}: {str(e)[:100]}... Switching to next model.")
            continue
    
    raise ValueError("All OpenRouter models failed.")


def _call_gemini(system_prompt, user_prompt):
    """Call Google Gemini API and return report text"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt + "\n\n" + user_prompt
    )
    return response.text


def _call_groq(system_prompt, user_prompt):
    """Call Groq API (Llama 3.3) and return report text"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    # Groq uses an OpenAI-compatible endpoint
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
    
    # Try 70B (Best Quality) -> 8B (High Speed/Rate Limit friendly)
    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=6000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"    ⚠️ Groq {model} failed: {str(e)[:100]}... Trying smaller model.")
            continue

    raise ValueError("All Groq models failed.")


def _run_all_models(system_prompt, user_prompt):
    """
    Run all available AI models and return list of (model_name, report_text, score).
    Does NOT raise on individual model failures.
    """
    models = [
        ("OpenRouter (Auto)", _call_openrouter),
        ("Google Gemini", _call_gemini),
        ("Groq (Llama 3.3)", _call_groq),
    ]

    results = []
    for model_name, call_fn in models:
        try:
            print(f"  → Calling {model_name}...")
            report_text = call_fn(system_prompt, user_prompt)
            score = extract_blueprint_score(report_text)
            verdict = extract_final_verdict(report_text)
            results.append({
                "model": model_name,
                "report": report_text,
                "score": score,
                "verdict": verdict,
                "error": None,
            })
            print(f"  ✅ {model_name}: Blueprint Score = {score}/100, Verdict = {verdict}")
        except Exception as e:
            error_msg = str(e)[:200]
            results.append({
                "model": model_name,
                "report": None,
                "score": 0,
                "verdict": "N/A",
                "error": error_msg,
            })
            print(f"  ❌ {model_name} failed: {error_msg}")

    return results


def _build_comparison_note(winner, all_results):
    """Build a short markdown note comparing model performance"""
    lines = [
        "",
        "---",
        "",
        "## AI Model Comparison",
        f"**Winning Model**: {winner['model']} (Blueprint Score: {winner['score']}/100)",
        "",
        "| Model | Blueprint Score | Verdict | Status |",
        "|---|---|---|---|",
    ]
    for r in sorted(all_results, key=lambda x: x["score"], reverse=True):
        if r["error"]:
            lines.append(f"| {r['model']} | N/A | N/A | ❌ Error: {r['error'][:80]} |")
        elif r["model"] == winner["model"]:
            lines.append(f"| **{r['model']}** | **{r['score']}/100** | **{r['verdict']}** | ✅ Winner |")
        else:
            lines.append(f"| {r['model']} | {r['score']}/100 | {r['verdict']} | Runner-up |")

    # Add brief analysis of why losers scored lower
    losers = [r for r in all_results if r["model"] != winner["model"] and r["report"]]
    if losers:
        lines.append("")
        lines.append("### Why Other Models Scored Lower")
        for r in losers:
            score_diff = winner["score"] - r["score"]
            if score_diff > 0:
                lines.append(f"- **{r['model']}** ({r['score']}/100): Scored {score_diff} points below the winner. "
                             f"Likely weaker in one or more weighted components (Scarcity, Liquidity, Sentiment, or Derivatives analysis depth).")
            elif score_diff == 0:
                lines.append(f"- **{r['model']}** ({r['score']}/100): Tied with the winner but was not selected as the primary (first model with highest score wins).")
            else:
                lines.append(f"- **{r['model']}** ({r['score']}/100): Comparable performance.")

    lines.append("")
    return "\n".join(lines)


def generate_report(token, date=None):
    """Generate a comprehensive token analysis report using all AI models, keeping the best one."""
    if date is None:
        date = datetime.date.today().isoformat()

    token_id = 'bitcoin' if token.lower() == 'btc' else 'ethereum' if token.lower() == 'eth' else token.lower()

    # ====================== FETCH DATA ======================
    cg = CoinGeckoAPI()
    try:
        market_chart = cg.get_coin_market_chart_by_id(id=token_id, vs_currency='usd', days=30)
        coin_info = cg.get_coin_by_id(id=token_id)
        tickers = cg.get_coin_ticker_by_id(id=token_id)
    except Exception as e:
        raise ValueError(f"Failed to fetch CoinGecko data for {token}: {str(e)}")

    # Prepare CoinGecko data
    prices = [p[1] for p in market_chart.get('prices', [])]
    volumes = [v[1] for v in market_chart.get('total_volumes', [])]
    market_caps = [m[1] for m in market_chart.get('market_caps', [])]

    # Liquidity metrics (from tickers)
    liquidity_data = []
    for ticker in tickers.get('tickers', [])[:5]:
        if ticker.get('base') == token.upper() and ticker.get('target') in ['USD', 'USDT']:
            liquidity_data.append({
                "exchange": ticker.get('market', {}).get('name'),
                "bid_ask_spread": ticker.get('bid_ask_spread_percentage'),
                "volume": ticker.get('converted_volume', {}).get('usd'),
            })

    # Compute derived metrics
    market_cap = coin_info.get('market_data', {}).get('market_cap', {}).get('usd', 0) or 0
    volume_24h = coin_info.get('market_data', {}).get('total_volume', {}).get('usd', 0) or 0
    liquidity_turnover_ratio = round(volume_24h / market_cap * 100, 4) if market_cap > 0 else 0

    data_summary = {
        "token_info": {
            "current_price": coin_info.get('market_data', {}).get('current_price', {}).get('usd'),
            "market_cap": market_cap,
            "24h_volume": volume_24h,
            "circulating_supply": coin_info.get('market_data', {}).get('circulating_supply'),
            "total_supply": coin_info.get('market_data', {}).get('total_supply'),
            "max_supply": coin_info.get('market_data', {}).get('max_supply'),
            "ath": coin_info.get('market_data', {}).get('ath', {}).get('usd'),
            "description": coin_info.get('description', {}).get('en', '')[:500],
            "genesis_date": coin_info.get('genesis_date'),
            "hashing_algorithm": coin_info.get('hashing_algorithm'),
        },
        "derived_metrics": {
            "liquidity_turnover_ratio_pct": liquidity_turnover_ratio,
            "volume_mcap_ratio": round(volume_24h / market_cap, 4) if market_cap > 0 else 0,
        },
        "30d_prices": prices,
        "30d_volumes": volumes,
        "30d_market_caps": market_caps,
        "liquidity": liquidity_data,
        "treasuries": fetch_treasuries(token),
    }

    # Add Coinglass data (OI, Funding, Liquidations)
    coinglass_key = os.getenv("COINGLASS_API_KEY")
    if coinglass_key:
        data_summary["derivatives"] = fetch_coinglass_data(token, coinglass_key)
        data_summary["liquidations"] = fetch_liquidation_data(token, coinglass_key)
    else:
        data_summary["derivatives"] = {"note": "Coinglass data skipped — COINGLASS_API_KEY not set"}
        data_summary["liquidations"] = {"note": "Liquidation data skipped — COINGLASS_API_KEY not set"}

    # Add Ultrasound for ETH
    if token.lower() == 'eth':
        ultrasound_data = fetch_ultrasound_data(token)
        if "error" not in ultrasound_data:
            data_summary["supply_dynamics"] = ultrasound_data
        else:
            data_summary["supply_dynamics"] = {"note": ultrasound_data["error"]}

    # Compute Kill Switch flags
    kill_switch_flags = compute_kill_switch_flags(data_summary)
    data_summary["kill_switch_flags"] = kill_switch_flags

    data_str = json.dumps(data_summary, indent=2)

    # ====================== GENERATE CHARTS ======================
    from io import BytesIO

    # Chart 1: Price and Volume
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot([p[0] for p in market_chart['prices']], prices, color='blue', label='Price (USD)')
    ax1.set_ylabel('Price', color='blue')
    ax2 = ax1.twinx()
    ax2.plot([v[0] for v in market_chart['total_volumes']], volumes, color='green', label='Volume (USD)')
    ax2.set_ylabel('Volume', color='green')
    plt.title(f"{token.upper()} 30-Day Price and Volume")
    plt.xlabel("Timestamp (ms)")
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    buffer1 = base64.b64encode(buffer.read()).decode()
    plt.close()

    # Chart 2: Market Cap
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot([m[0] for m in market_chart['market_caps']], market_caps, color='purple', label='Market Cap (USD)')
    plt.title(f"{token.upper()} 30-Day Market Cap")
    plt.xlabel("Timestamp (ms)")
    plt.ylabel("Market Cap")
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    buffer2 = base64.b64encode(buffer.read()).decode()
    plt.close()

    # Chart 3: Open Interest (if derivatives data available)
    buffer3 = None
    if "derivatives" in data_summary and "error" not in data_summary["derivatives"]:
        oi_data = data_summary["derivatives"].get("open_interest", [])
        if oi_data:
            times = [d.get('dateTime') for d in oi_data[-30:]]
            ois = [d.get('openInterest') for d in oi_data[-30:]]
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(times, ois, color='red', label='Open Interest')
            plt.title(f"{token.upper()} Recent Open Interest")
            plt.xlabel("Time")
            plt.ylabel("OI")
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            buffer3 = base64.b64encode(buffer.read()).decode()
            plt.close()

    # ====================== AI GENERATION (ALL MODELS) ======================
    blueprint_path = os.path.join(os.path.dirname(__file__), '..', 'blueprints', 'token-analysis-blueprint-v1.0.md')
    with open(blueprint_path, 'r', encoding='utf-8') as f:
        blueprint = f.read()

    user_prompt = f"Blueprint:\n{blueprint}\n\nData for {token.upper()} on {date}:\n{data_str}\n\nGenerate the full Forensic Audit Report now."

    print(f"\n📊 Running all AI models for {token.upper()}...")
    all_results = _run_all_models(SYSTEM_PROMPT, user_prompt)

    # Pick the best report by Blueprint Score
    successful = [r for r in all_results if r["report"]]
    if not successful:
        errors = "; ".join(f"{r['model']}: {r['error']}" for r in all_results)
        raise ValueError(f"All AI providers failed. Errors: {errors}")

    winner = max(successful, key=lambda x: x["score"])
    print(f"\n🏆 Winner: {winner['model']} with Blueprint Score {winner['score']}/100")

    report_md = winner["report"]

    # Append the model comparison note
    comparison_note = _build_comparison_note(winner, all_results)
    report_md += comparison_note

    # Embed charts
    report_md = report_md.replace('(price_chart)', f'(data:image/png;base64,{buffer1})')
    report_md = report_md.replace('(market_cap_chart)', f'(data:image/png;base64,{buffer2})')

    # ====================== SAVE (overwrite existing) ======================
    report_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', token)
    os.makedirs(report_dir, exist_ok=True)
    # Single file per token — always overwrite to keep reports current
    report_path = os.path.join(report_dir, 'audit-latest.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md)

    print(f"💾 Report saved to {report_path}")
    return report_path


def generate_combined_report(tokens, date=None):
    """Generate a combined report for multiple tokens"""
    if date is None:
        date = datetime.date.today().isoformat()
    combined_md = f"# Combined Report for {', '.join(t.upper() for t in tokens)} — {date}\n\n"
    for token in tokens:
        report_path = os.path.join(os.path.dirname(__file__), '..', 'reports', token, 'audit-latest.md')
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                combined_md += f"## {token.upper()} Section\n" + f.read() + "\n\n---\n\n"
        else:
            combined_md += f"## {token.upper()} Section\nReport not found for {token}.\n\n---\n\n"
    combined_path = os.path.join(os.path.dirname(__file__), '..', 'reports', f'combined-{"-".join(sorted(tokens))}-{date}.md')
    with open(combined_path, 'w', encoding='utf-8') as f:
        f.write(combined_md)
    return combined_path