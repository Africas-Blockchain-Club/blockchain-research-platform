# Research Team Folder – Africa's Blockchain Club

**Single source of truth** for all liquidity-first blueprints, forensic audit reports, dashboards, and AI tools.

---

## Quick Start (Most People)

1. **Clone the repo**
   ```bash
   git clone git@github.com:Africas-Blockchain-Club/PeterManda.git
   cd PeterManda/research-team
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate          # Linux/macOS/WSL
   # venv\Scripts\activate.bat      # Windows CMD
   # venv\Scripts\Activate.ps1      # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** (in the `research-team` root)
   ```env
   OPENROUTER_API_KEY=sk-or-...
   GOOGLE_API_KEY=AIza...                # Free from https://aistudio.google.com/app/apikey
   GROQ_API_KEY=gsk_...                  # From https://console.groq.com/
   COINGLASS_API_KEY=...                 # Optional (for derivatives data)
   ```

5. **Launch the dashboard**
   ```bash
   streamlit run dashboards/app.py
   ```

Open **http://localhost:8501** — you can now generate reports instantly.

---

## How to Use the Dashboard

### Generate New Reports (Recommended)
- Sidebar → **Generate Report**
- Select tokens (BTC, ETH, or both)
- Pick a date → click **Generate Reports**
- The system will:
  - Try **all AI models** (OpenRouter Premium, Google Gemini, Groq Llama 3.3)
  - **Auto-Fallback Logic**: Premium models (Claude 3.5 Sonnet) fail over to free versions automatically if credits are low.
  - Score each report using the Blueprint Score (0-100) based on 4 forensic phases.
  - Automatically select and save the **best** report
  - Add a "Model Comparison & Selection" section explaining why that model won

### View Reports
- Sidebar automatically shows all reports under **Report: Btc** and **Report: Eth**
- Click any report → view with charts + download PDF

---

## Full File Structure (February 2026)

```bash
research-team/
├── blueprints/
│   └── token-analysis-blueprint-v1.0.md
├── reports/
│   ├── btc/
│   │   └── audit-2026-02-12.md          ← always overwritten with latest best version
│   ├── eth/
│   │   └── audit-2026-02-12.md
│   └── combined-btc-eth-2026-02-12.md   ← removed (no longer generated)
├── dashboards/
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── assets/
├── data_engineering/
│   ├── pipelines/
│   ├── dags/
│   ├── config/
│   └── utils/
├── data_science/
│   ├── notebooks/
│   │   ├── exploratory/
│   │   └── production/
│   └── src/
├── data_analytics/
│   ├── metrics/
│   └── signals/
├── tools/
│   └── report_generator.py              ← AI engine with multi-model comparison
├── docs/
├── data/
│   ├── raw/
│   └── processed/
├── tests/
├── .github/
│   └── workflows/
├── .env
├── requirements.txt
├── README.md
└── (future task folders will follow the same pattern)
```

---

## AI Report Generation – Smart Multi-Model Logic (Feb 2026)

Every time you click **Generate Reports**, the system:

1. Runs **all three AI providers** in parallel:
   - OpenRouter (Auto) → Defaults to **Claude 3.5 Sonnet** (Premium), falls back to Free if needed.
   - Google Gemini 2.5 Flash (via latest `google-genai` SDK)
   - Groq (Llama 3.3 70B) → Falls back to Llama 3.1 8B on rate limits.

2. Extracts the **Blueprint Score** from each generated report

3. **Automatically selects the highest-scoring report**

4. Adds a **"Model Comparison & Selection"** section at the bottom explaining:
   - Which model won
   - The scores of all models
   - Why the chosen one was best

This ensures you always get the **highest quality, most blueprint-compliant** report possible.

---

## Prerequisites (One-time)

### System Dependencies (Linux/WSL)
```bash
sudo apt-get update
sudo apt-get install -y libcairo2-dev pkg-config python3-dev
```

---

## How to Add a New Task / Blueprint (Future-Proof)

1. Create new file → `blueprints/new-task-blueprint-v1.0.md`
2. Copy the structure from `token-analysis-blueprint-v1.0.md`
3. (Optional) Create matching folder in `reports/`
4. **No code changes needed** — the dashboard and AI engine auto-detect everything

**Current Active Blueprint**: Token Analysis v1.0 (liquidity-first forensic audits)

---

Maintained by Peter Manda & Africa’s Blockchain Club Research Team — February 2026

<!--
DEVELOPER NOTE (for Grok / future edits):
When user pastes this README again, remember:
- Core engine is in tools/report_generator.py (tries ALL models → picks highest Blueprint Score)
- Dashboard is dashboards/app.py (auto-detects blueprints/reports)
- Reports follow exact 4-Phase forensic structure + Model Comparison section
- Blueprints use naming: task-name-blueprint-v1.0.md
- reports/ uses sub-folders per token + always overwrites same file
Use this exact structure for any future edits or new tasks.
-->
```