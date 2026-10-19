# Changelog

All notable changes, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are build numbers (shown in the footer of every page).

## 2026.10.19-4

### Added
- The research page shows the free data and the paid AI write-up side by side from the start, with exactly what the write-up contains and what it costs. "Get the AI write-up" fetches the data and opens the payment step; report pages offer the write-up too.
- Order-book depth across large, established exchanges (CoinGecko tickers): the liquidity check now measures where a chain's coin actually trades, instead of one DEX pool.
- Open interest from the public futures APIs of OKX, Bitget, Gate and Hyperliquid (Binance and Bybit refuse cloud servers), so the leverage check has data without a paid Coinglass key.
- The server records which data sources answered on every 15-minute refresh and publishes the names (never error text) at /status/sources.json. The monitor reads it and emails when a source stops answering, so sources are judged from the server's location; some exchanges refuse other locations.

### Changed
- Token unlocks and holder concentration have no free, reliable source for a chain's coin. They are listed under "Not covered by these checks" with where to look, instead of counting as "No data" on every report. Eight checks remain.
- The page column is 100rem with gutters of at most 2rem, and card grids reach four across from 1400px wide.
- Featured reports rebuild as soon as the checks change, not when they next turn a day old.

### Fixed
- An order-book market with no pool (Hyperliquid's own spot exchange) was reported as a pool holding $0, which flagged thin liquidity. Missing liquidity now stays missing, and the report explains order books.
- The `site` link to a local build folder had been committed; it is untracked, and the ignore rules now match a link as well as a folder.

## 2026.10.19-3

### Fixed
- The site was swapped with two renames, leaving a moment with no site; it is now a symlink switched atomically to each complete build.
- The background refresher rebuilt the site after every featured report; it now rebuilds once per refresh, which kept a freshly started machine busy for minutes.
- The monitor names the page that fails, and retries a slow page once so a cold-starting machine is not reported as an outage.

## 2026.10.19-2

### Fixed
- CoinGecko rate limits left four featured reports without market data: featured chains now use their known CoinGecko ids (one request instead of two), and the adapter waits and retries after HTTP 429.
- Browsers asking for /favicon.ico got a 404; it now serves the logo.

### Added
- A report built while a source was down says so at the top, and records which source failed.
- The background refresher keeps a current data-only report for each featured chain (daily, or sooner when the last one was incomplete), never overwriting a paid AI write-up.

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
