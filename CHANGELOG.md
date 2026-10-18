# Changelog

All notable changes, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are build numbers (shown in the footer of every page).

## 2026.10.19-1

### Added
- Blockchain research: hand-checked profiles for Bitcoin, Ethereum, Solana, XRP Ledger, BNB Chain, Avalanche and Hyperliquid, live network data from public endpoints, and developer activity from GitHub.
- A static public site (home, blockchains, reports, method) served by Caddy, rebuilt after every report and every 15 minutes with fresh network data.
- Security standard: SECURITY.md, a threat model, Bandit, pip-audit, Gitleaks, CodeQL, Dependabot, actions pinned by commit, images pinned by digest, security headers.
- DevOps standard: protected main, pull-request workflow, staging deploys with an end-to-end check, production deploys after CI and security pass, a smoke test after every deploy, pre-commit hooks, a Makefile.
- Work Breakdown Structure, architecture decision records, code owners, pull request and issue templates.

### Changed
- Reports open with the blockchain (Phase 0) and then its native asset (Phase 1).
- The Streamlit app now holds only live research and the attack cost calculator, under /app.
- requests 2.34.2 and python-dotenv 1.2.4, fixing known vulnerabilities in the previous pins.

### Fixed
- Streamlit showed "Page not found" at /app/research; links now use the app root.
- Quoted news headlines no longer trip the advice-language check.

## 2026.10.18-5

### Added
- Payments in USDC or USDT on six networks, owner alerts, payer email delivery, the live-site monitor, the ABC brand.

## 2026.10.18-1

### Changed
- Rebuilt as an educational platform: risk checks instead of ratings, the data-only report, the advice-language check.
