# Changelog

All notable changes, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are build numbers (shown in the footer of every page).

## 2026.10.21-1

### Added
- Live prices on the site. The pages are rebuilt every 15 minutes, too slow for a price, so a new background job (`scripts/refresh_prices.py`) asks CoinGecko for the seven featured prices in one request every minute and writes `/status/prices.json`; the home, blockchains and chain pages read it once a minute while they are open, pause while the tab is hidden, and say when the prices were last updated. One request a minute however many visitors there are. `LIVE_PRICE_SECONDS=0` switches it off.

### Changed
- The Reports page and the home page show the seven featured blockchains and every AI write-up only. Data-only reports on other coins are snapshots that nothing refreshes, so they move into a "What people are researching" fold-out with each coin's searches in the last 30 days, when it was last researched and a link to any report, and the number of AI write-ups made so far. Searches are counted from the research and attack cost pages (new `searches` table, coin, name and time only, nothing about who searched).
- The Uniswap and Ethena sample reports are removed: they were tokens, not blockchains, and nothing kept them current. The Aave, Uniswap and Ethena reports were deleted from the live site.

### Security
- Pillow 12.3.0, which arrives through Streamlit, has advisories fixed only in Pillow 13, which no Streamlit release allows yet. They are triggered by opening crafted image, PDF or font files, and the platform never opens an image it did not ship. `scripts/audit_gate.py` accepts exactly these until 29 October 2026 (issue #16) and fails on anything else.

### Removed
- References to the weekly workshop sessions as if they were still running. The README notes, in the past tense, that the first features were built during the series, which has ended.

## 2026.10.20-1

### Added
- The attack cost page works out how a blockchain reaches agreement from CoinGecko's data instead of asking. A token that lives on another chain (AI Rig Complex on Solana, anything on Base or Arbitrum) is priced as an attack on that chain, with a note that the token has risks of its own; a mining algorithm means proof of work; a Cosmos ecosystem tag means CometBFT. "Proof of stake" alone does not say which kind, so the page still asks, and every detected answer can be changed.

- Every acronym is spelled out and explained before it is used. The attack cost page teaches each consensus design in full before its figures: Byzantine Fault Tolerance (what it stands for, the Byzantine Generals Problem, the fewer-than-a-third threshold and 3f + 1), proof of work and longest-chain proof of stake, each with primary sources (Lamport, Shostak and Pease 1982; the Bitcoin whitepaper; the CometBFT specification; Cardano's Ouroboros documentation). The research page, footers, reports, chain profiles (EVM, SHA-256, EIP-1559, layer 1) and the payment step follow the same rule, and AI write-ups are told to spell out every acronym with a plain explanation.

### Fixed
- A network read that fails is tried once more before it counts as a failed source. Hyperliquid's public RPC dropped the first request after a cold start on staging twice on 19 October, failing the end-to-end check although production was healthy.

## 2026.10.19-6

### Changed
- Paying for a write-up: the networks and coins this wallet can pay with come first, and the rest fold under "Other ways to pay". The pay button says what it is waiting for instead of turning grey, and the payment component uses ABC's palette and follows the app's light or dark theme.
- AI write-ups round their numbers (about $92.8 million, 97%), give the Rand equivalent only for the price, market cap and volume, replace a table whose values are all N/A with one sentence, and list only what each flagged risk check means, because the report page already shows every check as a card.

### Fixed
- The advice-language guard rejected a correct explanation of liquidation ("the exchange closes the position to stop losses exceeding the deposit") as a stop-loss instruction, which would discard a write-up the payer had paid for. The pattern now catches the order in every form but not the verb.
- While a paid write-up was being written, the old payment step stayed on screen greyed out beside the new one. The step is cleared once the payment verifies, and a "Payment confirmed" notice takes its place.

## 2026.10.19-5

### Added
- The attack cost calculator works for any blockchain, not only Ethereum. Pick one or type its full name; the price is live from CoinGecko, and the share of stake each attack needs follows the chain's consensus design, with a source for every figure. Proof-of-work chains and trusted validator lists (Bitcoin, XRP) are explained rather than priced, because buying coins does not attack them.
- Live staked totals and validator counts for Solana, Avalanche, Hyperliquid, Celestia and Cosmos Hub (`data_engineering/staking.py`, off switch `STAKING_DATA_ENABLED`), with the fewest validators that together hold a third and two thirds of stake. Ethereum, BNB Chain and Cardano ask for the staked total, with where to read it.
- A section on why smaller blockchains are easier to attack, with the Ethereum Classic attacks of August 2020 as the worked example, and a link to share each calculation. Each blockchain page on the site links to its own calculation.

### Changed
- The calculator counts the attacker's new stake in the total, so a third of stake takes half of what is staked today and two thirds takes twice it. A chain whose consensus design is not known asks the user to choose it instead of assuming one.

### Fixed
- Searching by a blockchain's full name found nothing unless the name was also its ticker: "Celestia" failed although CoinGecko lists Celestia (TIA). Full names, CoinGecko ids and tickers all work now, names with spaces such as "NEAR Protocol" are accepted, and a report is still stored once under its ticker.
- The ABC logo in the research app had no link in production (no `SITE_URL` was set) and Streamlit opens logo links in a new tab. It now returns to the home page in the same tab.
- A failed search repeated the name in capitals and was not written to the log; it now quotes the name as typed and is logged.

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
