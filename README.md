# Blockchain Research Platform

[![Deploy](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/deploy.yml/badge.svg)](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/deploy.yml)
[![Security](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/security.yml/badge.svg)](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/security.yml)
[![CodeQL](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/codeql.yml/badge.svg)](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/codeql.yml)
[![Monitor](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/monitor.yml/badge.svg)](https://github.com/Africas-Blockchain-Club/blockchain-research-platform/actions/workflows/monitor.yml)

Learn to research a blockchain. What is it for? How does it reach agreement, and what would an attacker need to control? How is its network running right now? And what does the public data on its native asset show? The platform answers with live data and explains every number, starting with seven blockchains: **Bitcoin, Ethereum, Solana, XRP Ledger, BNB Chain, Avalanche and Hyperliquid**.

**Live:** https://blockchain-research-platform.fly.dev

> **Educational research, not financial advice.** The platform never rates a blockchain or a coin, forecasts a price, or tells anyone to buy, sell or hold. See [docs/COMPLIANCE.md](docs/COMPLIANCE.md).

Built in the open by Peter Manda and Africa's Blockchain Club.

---

## Quick start

You need Python 3.10 or newer.

```bash
git clone https://github.com/Africas-Blockchain-Club/blockchain-research-platform.git
cd blockchain-research-platform
make install                 # .venv, dependencies and the git hooks
cp .env.example .env         # every setting is optional
make refresh                 # live data for the seven blockchains, and the static site
make dev                     # site on http://localhost:8000, research app on :8501
```

With an empty `.env` everything works except AI write-ups and payments, which are off until configured. From the command line:

```bash
python -m tools.report_generator "XRP Ledger" --data-only   # a full report, no AI, no cost
```

## How it works

```
Visitor ──HTTPS──> Fly.io ──> Caddy :8080 ─┬─ /        static site (sitegen/), instant
                                           └─ /app     Streamlit research app (dashboards/)
                                                          │
             tools/report_generator.py  <─────────────────┘
               ├─ Phase 0, the blockchain
               │    data_analytics/chains.py              hand-checked profiles, official sources
               │    data_engineering/networks.py          live blocks, fees, validators, throughput
               │    data_engineering/github_activity.py   developer activity
               ├─ Phase 1 onwards, the native asset
               │    data_engineering/fetchers.py          CoinGecko, DexScreener (by contract), DefiLlama
               │    data_analytics/risk_profile.py        eight rule-based risk checks, never summed
               └─ the write-up
                    data_analytics/data_report.py         data-only report (no AI)
                    data_science/llm.py, ai_generator.py  optional AI write-up
                    data_science/compliance.py            rejects anything that reads as advice
```

Paid AI write-ups take 2 US Dollars in USDC or USDT on Base, Arbitrum, Optimism, Polygon, BNB Chain or Ethereum, verified on-chain before anything runs (`payment_verifier.py`). The reasons behind each design choice are recorded in [docs/adr/](docs/adr/).

| Dependency | Module | When it is off or down |
|---|---|---|
| Anthropic (AI write-ups) | `data_science/llm.py` | Data-only reports |
| Public RPC nodes and APIs | `data_engineering/networks.py`, `fetchers.py` | "No data", never "Clear" |
| GitHub (developer activity) | `data_engineering/github_activity.py` | "No data" |
| Stablecoin payments | `payment_verifier.py` | Off by default; reports are free |
| SMTP (email) | `emailer.py` | Payments pause rather than charge without delivery |
| Postgres | `db.py` | Local SQLite |

## Engineering standards

| Area | What is in place | Where |
|---|---|---|
| Planning | Work Breakdown Structure with a dictionary and the 100% Rule; architecture decision records; changelog | [docs/WBS.md](docs/WBS.md), [docs/adr/](docs/adr/), [CHANGELOG.md](CHANGELOG.md) |
| Workflow | Protected `main`; every change by pull request with required checks; code owners; templates | [CONTRIBUTING.md](CONTRIBUTING.md), [.github/](.github/) |
| Quality | Over 100 offline tests, Ruff, pre-commit hooks running the same checks as CI | `tests/`, `.pre-commit-config.yaml`, `make check` |
| Delivery | Every pull request deployed to staging and checked end to end; merges deploy to production after CI and security pass; smoke test after each deploy | `.github/workflows/deploy*.yml` |
| Operations | Health checks through both servers; monitoring every 30 minutes with email alerts; daily volume snapshots | `scripts/monitor.py`, [deploy.md](deploy.md) |
| Security | Threat model; Bandit, pip-audit, Gitleaks and CodeQL on every pull request; Dependabot; actions pinned by commit and images by digest; strict content security policy and HSTS; unprivileged container | [SECURITY.md](SECURITY.md), [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) |
| Front end | ABC front-end standard: dark first, AA contrast, equal gutters at six widths, reduced motion respected | [docs/FRONTEND.md](docs/FRONTEND.md) |

## Project layout

```
config.py               every setting, read from .env
Caddyfile               front server: static site, /app proxy, security headers
Dockerfile, fly.toml    production image and deployment (fly.staging.toml for staging)
sitegen/                static site generator, templates and assets
dashboards/             Streamlit research app (research, attack cost)
data_engineering/       one adapter per outside service
data_analytics/         chain profiles, risk checks, the data-only report
data_science/           the AI adapter, the prompt, the advice-language check
tools/                  the pipeline, the report store, PDF export
scripts/                start-up, network refresher, monitor, payments report
blueprints/             the research protocol reports follow
tests/                  offline test suite
docs/                   WBS, ADRs, threat model, compliance and front-end notes
teaching/, x402/        standalone teaching examples, never deployed
```

## The build journey

The platform grows one feature per session of the Exclusive Friday Web3 and AI Workshop series; the lesson notes live in the [PeterManda repository](https://github.com/Africas-Blockchain-Club/PeterManda/tree/main/sessions): smart contracts (Session 2), Web3 identity and paying agents (Session 3), proof of stake and the cost of an attack (Session 4). [CHANGELOG.md](CHANGELOG.md) records each release since.

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Report vulnerabilities privately, as described in [SECURITY.md](SECURITY.md).

## Licence

MIT. See [LICENSE](LICENSE).
