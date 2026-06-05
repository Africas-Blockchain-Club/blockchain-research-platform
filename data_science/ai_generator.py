import os
import json
import re
import requests

# ====================== AI PROMPT ======================

SYSTEM_PROMPT = """You are a senior blockchain data scientist producing institutional-grade forensic audit reports.

CRITICAL RULES:
1. Write in British English throughout (recognise, realise, organised, colour).
2. Do NOT begin the report with any preamble or meta-commentary. Begin DIRECTLY with the report title.
3. Use the exact 5-phase structure below. YOU MUST USE THE EXACT HEADINGS PROVIDED (e.g. `## Phase 0: Overview & Narrative (The Social Layer)`). Do NOT change them to `1. Executive Summary`. If you break this, the Python tab parser will crash.
4. All currency values must be denominated in US Dollars ($) AND accompanied by an estimate in South African Rand (ZAR) in brackets.
5. NEVER use LaTeX math syntax (e.g., `\\\\frac{}`, `\\\\[ \\\\]`, or `$$ $$`). Use plain text markdown.

WRITING STYLE (MANDATORY — your output will be rejected if it sounds like AI):
- NEVER use contractions. Write "do not", "it is", "I am", "can not", "will not" — always.
- Use simple English. Write for a 13-year-old. If a simpler word exists, use it.
- Word replacements you MUST follow:
  "use" not "utilise", "show" not "demonstrate", "build" not "construct",
  "keep going" not "persevere", "make better" not "optimise", "speed up" not "accelerate",
  "comparing" not "dissecting", "split" not "bifurcate", "work together" not "collaborate".
- NEVER use em dashes (—). Rewrite the sentence or use a full stop instead.
- Write in flowing prose with paragraph breaks. Avoid excessive bullet points and numbered lists unless genuinely sequential.
- Be direct and specific. State facts plainly. Do not pad sentences with filler.

BANNED AI-SOUNDING WORDS AND PATTERNS (using these will get the report rejected):
- NEVER use: "delve", "tapestry", "landscape" (figuratively), "vibrant", "crucial", "pivotal",
  "testament", "underscore", "fostering", "garnered", "intricate", "interplay", "meticulous",
  "showcasing", "bolstered", "enduring", "enhancing", "groundbreaking", "nestled", "renowned",
  "diverse array", "rich tapestry", "evolving landscape", "indelible mark", "deeply rooted",
  "in the heart of", "a testament to", "serves as", "stands as", "boasts", "Additionally," (to start a sentence).
- NEVER write "Despite its [positive words], [subject] faces challenges..." — this is the most obvious AI pattern.
- NEVER write "Not just X, but also Y" parallelisms.
- NEVER overuse the rule of three ("adjective, adjective, and adjective").
- NEVER use vague attributions like "Experts argue", "Industry reports suggest", "Observers have cited".
- NEVER puff up importance with phrases like "marking a pivotal moment", "setting the stage for",
  "reflecting broader trends", "contributing to the", "highlighting its significance".
- Prefer "is" and "are" over "serves as", "stands as", "represents", "marks".
- Do NOT decorate headers or bullet points with emoji.
- Do NOT overuse boldface. Bold only the section headers and the Final Verdict rating.
- Write like a human analyst who has done the research and is explaining the findings to a colleague or client. Be plain, direct, and do not perform.
- For the Tokenomics and DeFi Mechanics sections, write in a professional and educationally friendly tone—like a senior analyst explaining something important to a client they respect. No jargon without explanation. Write for someone who understands investing but is new to DeFi.
- Where pie charts or doughnuts are requested, represent them visually using cleanly formatted markdown tables.

REPORT STRUCTURE (follow exactly, DO NOT RENAME THE `## Phase` sections):

# [TOKEN] Forensic Audit — [DATE]

## Phase 0: Overview & Narrative (The Social Layer)
### 0.1 High-Level Overview
- Outline the token's primary utility, sector, and narrative context based on available descriptions.
### 0.2 Social Sentiment & Mindshare
- Assess the sentiment, especially on X (Twitter), based on available context and current market trends (e.g., KOL interest, euphoric/panic phases, key catalysts).

## Phase 1: The Hard Data (Supply Forensics)
### 1.1 Tokenomics & Supply Dynamics
### 1.2 Sovereign & Institutional Inventory
- Table of "Verified Asset Inventory" classifying entities as Forced Sellers vs Strategic Holders
### 1.3 The "Permanent Scarcity" Layer
- Calculate Effective Supply using: Total Supply − (Dormant coins > 5yr) − (Burn addresses)
- For ETH: reference ultrasound.money burn data if provided
### 1.4 Behavioural Waves (HODL Analysis)
- Assess LTH vs STH behaviour signals (Distribution or Capitulation)
## Phase 1.5: Tokenomics & AMM Math
### 1.5.1 The Liquidity Pool Equation ($x \times y = k$)
- Using the data provided (liquidity_base_tokens and liquidity_quote_tokens), explicitly calculate the pool's Constant Product $k$.
- Show your work clearly: `[Base Token Qty] * [Quote Token Qty] = k`.
- Explain what happens to the price of the base token if a large market buy removes 10% of the base token supply from the pool.
### 1.5.2 Token Distribution (Visualisation)
- Use markdown tables or bulleted lists to cleanly represent the 'Pie Chart' or 'Doughnut' split of the Tokenomics (e.g. % in LP, % Team, % Treasury) if known. If exact tokenomics are missing, just show the Pool split (Base % vs Quote %).

## Phase 2: Market Structure (The Liquidity Layer)
### 2.1 Liquidity & Order Book Depth
- Analyse liquidity metrics: Turnover Ratio, depth, spread, slippage
- Stress Test: simulate $1M, $5M, $10M market sell impact
### 2.2 Liquidity Assessment
- Why liquidity matters for this specific token
### 2.3 Cost Basis Analysis
- Realised Price assessment, STH cost basis signal

## Phase 2.5: DeFi Mechanics
### 2.5.1 AMM Infrastructure & Routing
- Explain in simple terms how the trading mechanics for this token function. 
- Mention the difference between Automated Market Makers (AMMs) and traditional order books. 
- Briefly discuss Slippage, Price Impact, and what they mean for evaluating this specific token based on its current liquidity depth.

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

def extract_blueprint_score(report_text):
    """Extract the Blueprint Score from the generated report."""
    score_patterns = [
        r'\*{0,2}Total\*{0,2}\s*\|[^|]*\|\s*\*{0,2}(\d{1,3})\s*/\s*100\*{0,2}',
        r'Blueprint\s+Score[^\n]*?\*{0,2}(\d{1,3})\s*/\s*100\*{0,2}',
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
    """Extract the Final Verdict rating from the generated report."""
    verdict_options = r'(Strong\s+Buy|Accumulate|Neutral|Distribute|Strong\s+Sell)'
    patterns = [
        r'\*{0,2}Rating\*{0,2}\s*:\s*\*{0,2}' + verdict_options + r'\*{0,2}',
        r'(?:Final\s+)?Verdict[^:]*:\s*\*{0,2}' + verdict_options + r'\*{0,2}',
    ]
    for pattern in patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            return re.sub(r'\s+', ' ', match.group(1).strip())
    return "Unknown"

def _call_openrouter(system_prompt, user_prompt, model="openrouter/free"):
    """Call OpenRouter API and return report text"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"OpenRouter API error {response.status_code}: {response.text}")

def _call_gemini_native(system_prompt, user_prompt, model="gemini-2.5-pro"):
    """Call Google Gemini Native API directly"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in .env")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    data = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [{
            "parts": [{"text": user_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2
        }
    }
    
    response = requests.post(url, json=data, timeout=60)
    
    if response.status_code == 200:
        try:
            parts = response.json()['candidates'][0]['content']['parts']
            # Gemini 2.5 Flash/Pro may return a "thinking" part first, then the actual content.
            # Always take the LAST text part (the actual report), not the first (thinking).
            text_parts = [p['text'] for p in parts if 'text' in p]
            report_text = text_parts[-1] if text_parts else ""
            # If the model leaked its thinking into the text, strip everything before the report title
            if report_text.startswith("Okay") or report_text.startswith("Let me") or report_text.startswith("First"):
                # Find the actual report start (markdown heading)
                heading_match = re.search(r'^#\s', report_text, re.MULTILINE)
                if heading_match:
                    report_text = report_text[heading_match.start():]
            return report_text
        except KeyError:
            raise Exception(f"Gemini API returned unexpected structure: {response.text}")
    else:
        raise Exception(f"Gemini API error {response.status_code}: {response.text}")

def _call_groq_native(system_prompt, user_prompt, model="meta-llama/llama-4-maverick-17b-128e-instruct"):
    """Call Groq Native API directly — uses Llama 4 Maverick (flagship)"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env")
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"Groq API error {response.status_code}: {response.text}")

def generate_ai_report(token, data_summary, kill_switches, model="google/gemini-2.5-pro"):
    """
    Generates the final token analysis markdown report using a specific model.
    Pass in the data dicts from data_engineering and data_analytics.
    """
    from datetime import datetime
    date_str = datetime.now().strftime("%d %b %Y")
    
    user_prompt = f"""
    Generate a concise forensic audit report for {token.upper()}.
    Today's Date: {date_str}
    Exchange Rate context: 1 USD = 19 ZAR.

    CRITICAL DATA INSTRUCTION:
    The field "recent_news_headlines" contains REAL, CURRENT news headlines fetched from CryptoPanic right now.
    These are not fabricated. In Phase 0.2 (Social Sentiment), you MUST cite specific headline titles from this field by name.
    If a headline mentions an investment, partnership, listing, or exploit, that IS the catalyst to discuss.
    Do not write vague sentiment summaries when you have actual news in front of you.

    ====== EXTRACTED DATA SUMMARY ======
    {json.dumps(data_summary, indent=2)}

    ====== KILL SWITCH FLAGS ======
    {json.dumps(kill_switches, indent=2)}

    If any field shows "Data Unavailable" or an error, state it plainly and estimate using what IS available.
    Do not fabricate numbers that are not in the data.
    """
    
    report_text = None
    
    if "gemini" in model.lower():
        # Clean model name for native Gemini (e.g. google/gemini-2.5-flash -> gemini-2.5-flash)
        clean_model = model.split("/")[-1] if "/" in model else model
        report_text = _call_gemini_native(SYSTEM_PROMPT, user_prompt, model=clean_model)
    elif "groq" in model.lower() or "llama" in model.lower() or "qwen" in model.lower():
        # Route to Groq native API
        if "qwen" in model.lower():
            groq_model = "qwen/qwen3-32b"
        else:
            groq_model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        report_text = _call_groq_native(SYSTEM_PROMPT, user_prompt, model=groq_model)
    else:
        # Fall back to OpenRouter for explicitly openrouter models
        report_text = _call_openrouter(SYSTEM_PROMPT, user_prompt, model=model)

    # ---- Universal safety net: strip any thinking/reasoning preamble ----
    # Some models (especially Gemini, Qwen) leak chain-of-thought before the report.
    if report_text:
        # Qwen3 wraps its reasoning in <think>...</think> tags — remove them entirely
        report_text = re.sub(r'<think>.*?</think>', '', report_text, flags=re.DOTALL).strip()
        # The real report always starts with a markdown heading (# Token Forensic Audit).
        heading_match = re.search(r'^#\s', report_text, re.MULTILINE)
        if heading_match and heading_match.start() > 0:
            report_text = report_text[heading_match.start():]
    
    return report_text
