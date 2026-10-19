# The Blockchain Research Protocol (v3.0)

**Educational research on a token and the blockchain it lives on**

**Objective**: produce a research report on **[TOKEN]** that teaches the reader how to read the public data about it: the project and its news, its supply, how its main exchange pool sets the price, its liquidity, its use in DeFi, its leveraged trading, and the long-term factors worth watching.

**What the report is not**: it is not financial advice. It never rates the token, never forecasts a price, and never tells the reader to buy, sell or hold. Ratings and recommendations are financial advice, which needs a licence (in South Africa, authorisation from the Financial Sector Conduct Authority under the FAIS Act). See `docs/COMPLIANCE.md`.

**Audience**: software engineering students and community members learning to research blockchains. Every table is followed by a callout (`> **Reading this table:** ...`) and every technical term is defined the first time it appears.

**Format rules**: plain-text maths only (for example `100 / 50 = 2`; LaTeX breaks the PDF), British English, no contractions, no long dashes, and currency in US Dollars with the Rand equivalent in brackets.

---

## The Research Method

Every report walks the Research section of the Africa's Blockchain Club curriculum:

1. **Define the question** - what does the learner want to understand about this token?
2. **Identify sources** - where does trustworthy data live, and what does each source measure?
3. **Analyse the technology** - the chain, the protocol, and how the token trades.
4. **Study market data** - supply, liquidity, derivatives.
5. **Evaluate the team and community** - developer activity and public narrative.
6. **Assess regulatory exposure** - what regulators have said about the project.
7. **Perform a SWOT analysis** - strengths, weaknesses, opportunities and threats of the project.
8. **Document findings** - the facts, the risk checks, and the open questions, never a verdict.

---

## Report Structure

The `## Phase` headings are a contract with the dashboard, which turns each one into a tab. `data_science/ai_generator.py` checks they are all present before a write-up is saved. Rename them in both places or not at all.

| Section | What it covers |
|---|---|
| How to Read This Report | What each phase answers, and that the report teaches rather than judges |
| Phase 0: Overview and Narrative | Snapshot tables, recent headlines, and the economic factors that have moved crypto prices in the past, with where to check their current values |
| Phase 1: Supply | Circulating, total and maximum supply; distribution and vesting; what limits or expands supply |
| Phase 1.5: Exchange Pool Maths | The constant product formula (x multiplied by y equals k) worked through with the real pool balances |
| Phase 2: Market Structure | Liquidity, turnover, depth, and what sales of different sizes would do to the price in the main pool |
| Phase 2.5: DeFi Mechanics | Total value locked (TVL), protocol category, and how trading the token works |
| Phase 3: Derivatives | Open interest, funding and liquidations, explained |
| Phase 4: What the Data Shows | A summary of facts, the risk checks explained, a SWOT table, and questions to research further |
| Phase 5: Long-Term Factors to Watch | Chain, protocol and supply metrics to track over time, and developments that would strengthen or weaken the project, with no probabilities and no price effects |
| Risk Checks | Written by code, not by the model: eight rule-based checks, plus the topics they do not cover |
| Sources and Limitations | Written by code: every source, the snapshot time, and which model wrote the explanations |

---

## The Risk Checks

The risk checks replace the Blueprint Score and the Buy/Sell verdict used up to v2.0. Each check has three possible results: **Flagged**, **Clear** or **No data**. Missing data is never treated as clear. The checks are never added into a score, because a total would recreate a rating.

| Check | Teaching threshold |
|---|---|
| Unusually high trading volume | More than 100% of market cap traded in 24 hours |
| Thin on-chain liquidity | Less than 1% of market cap in the main DEX pool |
| Large future supply (dilution) | Fully diluted value more than 3 times market cap |
| Most supply not yet circulating | Less than 50% of supply circulating |
| Large token unlock in the next 30 days | More than 15% of supply unlocking within 30 days |
| Supply held by a few wallets | Top 10 wallets holding more than 80% of supply |
| Not tracked by major data sites | Absent from both CoinGecko and CoinMarketCap |
| Large fall from all-time high | Price more than 70% below its all-time high |
| Large price swing in 30 days | Price moved more than 30% up or down in 30 days |
| Heavy leveraged trading | Open interest above 10% of market cap |

The thresholds are teaching thresholds chosen by this platform to make patterns visible. They are not industry standards. The code lives in `data_analytics/risk_profile.py`.

---

## Two Ways to Produce a Report

- **Data-only report** (`data_analytics/data_report.py`): built by code from the fetched data. No API key, no cost, no model-written text. This is the floor that is always available.
- **AI write-up** (`data_science/ai_generator.py`): a model explains the same data in the structure above. It passes a structure check and an advice-language check (`data_science/compliance.py`) before it is saved. A write-up that fails either check is rejected, and nothing is saved.

---

## Sources

| Source | What it provides |
|---|---|
| CoinGecko | Market cap, supply, price history, project description, contract addresses, exchange rate |
| DexScreener | The main exchange pool, found by the token's contract address |
| CoinMarketCap | Listing check only |
| Google News RSS | Recent headlines |
| DefiLlama | Total value locked for the chain or protocol |
| Coinglass | Open interest and liquidations (needs an API key) |
| Ultrasound.money | ETH burn data |

---

## Version History

- v1.1 (Feb 2026): four-phase forensic framework with a Blueprint Score and Kill Switch checklist.
- v2.0 (Jul 2026): widened from the token to the blockchain; added macro context, AMM maths, DeFi mechanics, phase signals, a Buy/Sell verdict and a Long-Term Conviction Score.
- v3.0 (Oct 2026): rewritten as education, not advice. Removed the Blueprint Score, the Conviction Score, phase signals, the verdict, entry and exit triggers and scenario probabilities. Added the rule-based risk checks, the data-only report, the advice-language check, and pool lookup by contract address.
