# Research Team: Africa's Blockchain Club

Single source of truth for liquidity-first forensic audit reports, the Streamlit dashboard, and the AI tooling behind both.

---

## Quick Start

1. **Clone the repo**
   ```bash
   git clone git@github.com:Africas-Blockchain-Club/PeterManda.git
   cd PeterManda/research-team
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate          # Linux/macOS/WSL
   # venv\Scripts\activate.bat       # Windows CMD
   # venv\Scripts\Activate.ps1       # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium       # one-time; needed for chart screenshots
   ```

4. **System dependencies (Linux/WSL, one-time)**
   ```bash
   sudo apt-get install -y libcairo2-dev pkg-config python3-dev
   ```

5. **Create `.env`** (in the `research-team` root)
   ```env
   ANTHROPIC_API_KEY=sk-ant-...       # required; the only model provider in use

   # Optional
   COINGLASS_API_KEY=...              # derivatives data (funding, liquidations)
   COINGECKO_API_KEY=CG-...           # raises CoinGecko rate limit from 30 to 500 req/min
   REDDIT_CLIENT_ID=...                # subreddit subscriber counts
   REDDIT_CLIENT_SECRET=...
   ```
   See `.env.example` for the full list, including Reddit setup steps. Note that `OPENROUTER_API_KEY`, `GOOGLE_API_KEY`, and `GROQ_API_KEY` are leftover from an earlier multi-model version; no code path reads them. Only `ANTHROPIC_API_KEY` is required.

6. **Launch the dashboard**
   ```bash
   streamlit run dashboards/app.py
   ```

Open **http://localhost:8501**.

---

## How the Dashboard Works

### Overview
The landing page shows a live card grid of the ten most recently generated reports, each with its Blueprint Score, Verdict, and an age indicator (green under three days, amber under a week, red beyond that).

### Generate Report
- Select tokens from the auto-refreshing top-10-by-utility list, or type a custom ticker.
- Pick a model depth: `claude-haiku-4-5` (fastest), `claude-sonnet-4-6` (thorough, default), or `claude-opus-4-8` (deepest).
- Click **Generate Reports**. The pipeline fetches data, computes metrics, runs the AI, extracts the score and verdict, and writes the report to `reports/{TOKEN}_audit_report.md`.
- After generation, an **AI Investment Brief** panel appears: a short, plain-English summary in Peter's voice (drawn from `/resources/`), generated on demand at the same three depth tiers, optionally tailored to a named audience.

### View Reports
Click any report card or sidebar shortcut to view the full markdown with embedded chart screenshots, or download it as a PDF.

---

## Architecture

```
dashboards/app.py
       │
       └─► tools/report_generator.py        (orchestrator)
                │
                ├─► data_engineering/fetchers.py        (DexScreener, CoinGecko, CoinGlass,
                │                                         DefiLlama, Ultrasound.money, CryptoPanic news)
                ├─► data_engineering/screenshot_bot.py  (Playwright chart screenshots)
                ├─► data_analytics/metrics.py           (liquidity turnover, Kill Switch flags)
                └─► data_science/ai_generator.py        (Anthropic Claude report generation)
                         │
                         └─► data_science/anthropic_analyst.py  (AI Investment Brief, separate and on-demand)
```

There is a single model provider, Anthropic Claude, selectable per request at three depth tiers (Haiku/Sonnet/Opus). There is no multi-model race; the model chosen in the dashboard is the model that writes the report.

**Token aliasing**: `report_generator.normalise_token()` maps common full names to their ticker (`SOLANA` → `SOL`, `ETHEREUM` → `ETH`, and so on) so a report is never duplicated under two names.

**Report output**: saved as `reports/{TOKEN}_audit_report.md` with a YAML-style header the dashboard reads without scanning the full body:
```
---
Token: ETH
Score: 67
Verdict: Accumulate
Model: claude-sonnet-4-6
Screenshot: data/images/ETH_chart.png
---
```
Score and verdict are extracted from the report text with a chain of regex patterns; if the AI never writes a readable Final Verdict line, the verdict is inferred from the score band instead (`infer_verdict_from_score` in `data_science/ai_generator.py`).

**Blueprint**: `blueprints/token-analysis-blueprint-v1.0.md` defines the five-phase forensic structure (Phase 0 Overview & Narrative, Phase 1 Supply Forensics, Phase 2 Market Structure, Phase 3 Derivatives & Sentiment, Phase 4 Synthesis & Blueprint Score), plus a Kill Switch checklist (thin order books, supply unlock cliffs, concentration risk, wash trading) and a source layer. The system prompt in `data_science/ai_generator.py` enforces this structure exactly; phase headings must not be renamed or the dashboard's tab parser breaks.

**Adding a new task or blueprint**: create `blueprints/new-task-blueprint-v1.0.md` following the existing structure. No code changes are needed; the dashboard auto-detects any blueprint file.

---

## File Structure

```
research-team/
├── blueprints/
│   └── token-analysis-blueprint-v1.0.md
├── reports/
│   └── {TOKEN}_audit_report.md          ← one file per token, overwritten on regeneration
├── dashboards/
│   └── app.py                           ← Streamlit UI
├── data_engineering/
│   ├── fetchers.py                      ← DexScreener, CoinGecko, CoinGlass, DefiLlama, news
│   └── screenshot_bot.py                ← Playwright chart capture
├── data_analytics/
│   └── metrics.py                       ← liquidity metrics, Kill Switch flags
├── data_science/
│   ├── ai_generator.py                  ← forensic report generation (Anthropic)
│   └── anthropic_analyst.py             ← AI Investment Brief (Anthropic, voice-matched)
├── tools/
│   └── report_generator.py              ← pipeline orchestrator
├── data/
│   └── images/                          ← chart screenshots, one per token
├── x402/                                ← standalone x402 payment protocol demo (local anvil testnet, unrelated to the audit pipeline)
├── .env
├── requirements.txt
└── README.md
```

---

## x402 Demo

`x402/` is a self-contained demo of the x402 payment protocol against a local Anvil testnet: a mock paywall server (`mock_server.py`) and a CLI wallet client (`demo.py`). It is unrelated to the audit pipeline and shares only the virtual environment. See the docstrings in `x402/demo.py` and `x402/mock_server.py` for run instructions.

---

Maintained by Peter Manda & Africa's Blockchain Club Research Team.
