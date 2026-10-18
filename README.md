# Blockchain Research Platform

Learn to read a crypto token. Pick a token, pull its public data, see which risk checks it trips, and read a report that explains what every number means.

> **Educational research, not financial advice.** This platform never rates a token, forecasts a price, or tells anyone to buy, sell or hold. See [docs/COMPLIANCE.md](docs/COMPLIANCE.md) for why, and for the rules every fork must keep.

Built in the open by Peter Manda and Africa's Blockchain Club, with AI assistance (Anthropic's Claude). Every commit records the collaboration on purpose: using AI well means directing it, checking it, and saying so.

---

## Quick start

You need Python 3.10 or newer.

```bash
git clone https://github.com/Africas-Blockchain-Club/blockchain-research-platform.git
cd blockchain-research-platform

python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
cp .env.example .env                   # every setting is optional

streamlit run dashboards/app.py        # opens http://localhost:8501
```

That is enough to research any token and save **data-only reports**. No API key is needed and nothing costs money.

Optional extras:

- **AI write-ups**: set `ANTHROPIC_API_KEY` in `.env`.
- **Chart screenshots**: run `playwright install firefox` once. On Linux or WSL you may also need `sudo apt-get install -y libcairo2-dev pkg-config python3-dev` for the PDF export.
- **Derivatives data**: set `COINGLASS_API_KEY`.

From the command line:

```bash
python -m tools.report_generator SOL --data-only   # free, no AI
python -m tools.report_generator SOL               # AI write-up when AI is on
```

---

## How it works

```
dashboards/app.py                    Streamlit app: Home, Research, Reports, Attack cost, How it works
   │
   └─► tools/report_generator.py     the pipeline
         │
         ├─ Stage 1, free, no AI
         │   ├─► data_engineering/fetchers.py      CoinGecko, DexScreener (by contract address),
         │   │                                     DefiLlama, Coinglass, Google News, exchange rate
         │   ├─► data_engineering/screenshot_bot.py chart screenshot (optional)
         │   └─► data_analytics/risk_profile.py    ten rule-based risk checks
         │
         └─ Stage 2, one of
             ├─► data_analytics/data_report.py     data-only report, built by code
             └─► data_science/ai_generator.py      AI write-up, through data_science/llm.py
                   └─► data_science/compliance.py  rejected if it reads as advice
                                │
                     tools/report_store.py         reports/{TOKEN}_research_report.md and .json
```

**The risk checks** replace a score. Each one compares one number with a teaching threshold and comes back **Flagged**, **Clear** or **No data**. They are never added together. The full list is in the [research protocol](blueprints/blockchain-research-protocol-v3.0.md).

**The AI is optional.** Every external dependency sits behind one module with an off switch:

| Dependency | Module | Off switch | When it is off |
|---|---|---|---|
| Anthropic (AI write-ups) | `data_science/llm.py` | `AI_ENABLED=false` or no key | Data-only reports |
| Playwright (screenshots) | `data_engineering/screenshot_bot.py` | `SCREENSHOTS_ENABLED=false` | No chart in the report |
| Base Sepolia (payment demo) | `payment_verifier.py` | `PAYMENTS_ENABLED=false` (default) | Reports are free |
| SMTP (email) | `emailer.py` | Leave `SMTP_*` empty | No email; the report stays in the app |
| Postgres | `db.py` | Leave `DATABASE_URL` empty | Local SQLite file |

All settings are read in one place, `config.py`. See `.env.example` for the full list.

---

## Make it yours

A fork for a class or a project changes the brand in `.env` (`BRAND_NAME`, `BRAND_SHORT`, `APP_NAME`, `BRAND_ACCENT`) and the matching `primaryColor` in `.streamlit/config.toml`. Nothing else needs to change.

Good first projects:

- Connect a token-unlock data source and turn the unlock check from "No data" into a real result.
- Connect an on-chain holder data source for the concentration check.
- Add a risk check of your own, following the rules in [docs/COMPLIANCE.md](docs/COMPLIANCE.md).
- Add a page that compares how the same check reads across several tokens, without ranking them.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before you open a pull request.

---

## The build journey

This platform grows one feature per session of the Exclusive Friday Web3 and AI Workshop series. The lesson notes live in the original repository:

| Session | Topic | What the platform gained | Lesson notes |
|---|---|---|---|
| 2 | Smart contracts and security | The first deployed contracts | [Session 2](https://github.com/Africas-Blockchain-Club/PeterManda/blob/main/sessions/session-2-smart-contracts-and-security.md) |
| 3 | Web3 and Web2 identity, self-custody, AI agents that pay | Wallet payments, wallet sign-in, email delivery, the `x402/` agent-payment demo | [Session 3](https://github.com/Africas-Blockchain-Club/PeterManda/blob/main/sessions/session-3-identity-self-custody-and-paying-agents.md) |
| 4 | Proof of stake, the cost of attacking a chain, rollups | The Attack cost page | [Session 4](https://github.com/Africas-Blockchain-Club/PeterManda/blob/main/sessions/session-4-proof-of-stake-attack-cost-rollups-and-ai-compute.md) |
| Oct 2026 | Education, not advice | Risk checks instead of a score, the data-only report, the advice-language check, the front-end standard, tests and CI | [docs/COMPLIANCE.md](docs/COMPLIANCE.md) |

---

## Project layout

```
blockchain-research-platform/
├── config.py                 every setting, read from .env
├── db.py                     payments and reports (Postgres or SQLite)
├── payment_verifier.py       on-chain check for the testnet payment demo
├── emailer.py                the only SMTP code
├── blueprints/               the research protocol the reports follow
├── dashboards/
│   ├── app.py                entry point and navigation
│   ├── ui/                   theme, shared components, PDF export, wallet components
│   ├── views/                one module per page
│   ├── wallet_pay/           browser wallet payment component (plain HTML)
│   └── wallet_connect/       browser wallet sign-in component (plain HTML)
├── data_engineering/         fetchers and the screenshot adapter
├── data_analytics/           metrics, risk checks, the data-only report
├── data_science/             the AI adapter, the prompt, the advice-language check
├── tools/                    the pipeline and the report store
├── reports/                  saved reports (.md for people, .json for the app)
├── tests/                    pytest suite, no network and no API calls
├── docs/                     compliance and front-end notes
├── teaching/                 standalone teaching examples
└── x402/                     standalone x402 payment protocol demo (pip install -r requirements-x402.txt)
```

---

## Development

```bash
pytest            # runs offline; AI and payments are forced off in tests
ruff check .
```

Continuous integration runs both on every push and pull request (`.github/workflows/ci.yml`).

Deployment notes are in [deploy.md](deploy.md).

---

## Licence

MIT. See [LICENSE](LICENSE).

---

Maintained by Peter Manda and the Africa's Blockchain Club research team.
