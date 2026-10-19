---
Token: SOL
Mode: data
Model: none
Generated: 2026-10-19T05:06:54.686784+00:00
Format: 3
---

# Solana (SOL) Blockchain Research Report - 19 October 2026

> **Educational research, not financial advice.** This report explains what public data says about a blockchain and its native asset so that you can learn to read it. It does not recommend buying, selling or holding any crypto asset, and it does not take your circumstances into account. Africa's Blockchain Club is not an authorised financial services provider. Crypto assets are high risk and their price can fall to zero. Before you invest, speak to a financial services provider authorised by the Financial Sector Conduct Authority (FSCA).


## How to Read This Report

> This is the data-only version of the report: every number comes straight from the sources listed at the end, and no AI wrote any of it. Phase 0 explains the blockchain itself: what it is for, how it reaches agreement, and how its network is running right now. Phase 1 turns to its native asset: price, market size and supply. Phase 1.5 and Phase 2 show how its main exchange pool and the large exchanges' order books set the price. Phase 3 covers leveraged trading. The risk checks then compare the data with teaching thresholds. A check that says "No data" means the platform could not measure it, not that the risk is absent.

## Phase 0: The Blockchain

### 0.1 What It Is For

A single fast chain designed for high throughput and low fees, so that payments, trading and consumer apps can run without a separate scaling layer.

| Question | Answer |
|---|---|
| Launched | March 2020 (mainnet beta) |
| How it reaches agreement | Proof of stake, with Proof of History: a running cryptographic clock that orders transactions before validators vote on them. |
| What can be built on it | Smart contracts are called programs, usually written in Rust. Transactions that touch different accounts run in parallel. |
| What the native asset does | SOL pays fees and is staked to validators. New SOL is issued to stakers at a rate that falls over time, and part of each fee is burned. |
| Main uses today | Payments and stablecoin transfers, Decentralised trading, Consumer apps, Token launches |

> **Reading this table:** the consensus method decides who can add blocks and what an attacker would need to control. The native asset's role tells you why anyone needs to hold it.

Check these facts at the source: https://solana.com/docs, https://solana.com/solana-whitepaper.pdf.

### 0.2 The Network Right Now

| Measure | Value | What It Means |
|---|---|---|
| Transactions per second (all) | 4,672 | Includes validators' own vote transactions, which make up most of Solana's traffic. |
| Transactions per second (users) | 1,582 | Non-vote transactions only: the activity people and programs actually create. |
| Average slot time | 0.215 seconds | How often a validator gets the chance to add a block. |
| Current epoch | 1,061 | Epochs are the periods after which stake and rewards are recalculated. |

Source: Public JSON-RPC endpoint (https://api.mainnet-beta.solana.com). Read at the time of this report; the network keeps moving.

### 0.3 Building and Use

| Measure | Value | What It Means |
|---|---|---|
| Main client repository | [anza-xyz/agave](https://github.com/anza-xyz/agave) | The software most of the network's computers run |
| Commits in the last 4 weeks | 393 | Code changes accepted recently. Steady work is a sign of a maintained network |
| Last change | 18 October 2026 | When the repository last changed |
| Stars | 1,958 | Public interest from developers, not quality |
| Value locked in its apps (TVL) | $5,902,641,088 (R97,098,445,890) | Money deposited in apps built on this chain: a sign of real use |

> **Reading this table:** developer numbers come from one main repository on GitHub. Many chains develop across several repositories, some partly in private, so treat this as a partial view of the effort, not a measure of success.

### 0.4 Recent News Headlines

| Headline | Source | Published |
|---|---|---|
| Solana (SOL) Price News Today: SOL Speed Upgrade Lands October 21, While Pepeto Buyers Rush In Fast | StreetInsider | Mon, 19 Oct 2026 04:47:58 GMT |
| Analysts Pick One Altcoin Above Bitcoin and Solana, But It's Falling Anyway | BeInCrypto | Sun, 18 Oct 2026 22:00:00 GMT |
| Solana forecast: 22.88 million new SOL a year | CryptoTicker | Sun, 18 Oct 2026 21:34:34 GMT |
| Is Solana Too Cheap to Ignore at Today's Prices? | The Motley Fool | Sun, 18 Oct 2026 16:57:00 GMT |
| Is Solana Too Cheap to Ignore at Today's Prices? | Yahoo Finance | Sun, 18 Oct 2026 16:17:00 GMT |
| Spot Ripple (XRP) ETFs Reach the End of an Era, Solana (SOL) Funds Can’t Catch a Break | CryptoPotato | Sun, 18 Oct 2026 15:36:00 GMT |
| Solana Now Holds $15.5 Billion in Stablecoins. How Far Behind Ethereum Is It? | 24/7 Wall St. | Sun, 18 Oct 2026 13:57:00 GMT |
| Solana’s burn rate hits highest since 2025 – What could it mean for SOL/ETH? | AMBCrypto | Sun, 18 Oct 2026 10:00:40 GMT |

> **Reading this table:** headlines show what people are talking about, not what is true. Open the source and check who is making each claim.

## Phase 1: The Native Asset

### 1.1 Snapshot

| Name | Symbol | Price | 24h Change | 7d Change | 30d Change |
|---|---|---|---|---|---|
| Solana | SOL | $105 (R1,732) | 1.55% | -6.88% | -6.28% |

| Market Cap | Fully Diluted Value | All-Time High | Change From All-Time High |
|---|---|---|---|
| $62,056,344,377 (R1,020,826,865,002) | $66,961,449,601 (R1,101,515,845,936) | $293 | -64.11% |

> **Reading this table:** market cap is price multiplied by circulating supply. Fully diluted value uses the maximum supply instead, so the gap between the two shows how many coins are still to come.

### 1.2 How the Project Describes Itself

> Solana is a high-performance Layer 1 blockchain designed for mass adoption by providing a fast, secure, and low-cost environment for decentralized applications. It distinguishes itself by scaling globally without the use of complex sharding or multiple layers, instead maintaining a single, unified ledger to avoid liquidity fragmentation. This architecture allows it to process thousands of transactions per second with sub-second finality, often at a cost of less than a penny per transaction. The network operates on a unique hybrid model that combines Proof of Stake with an innovation called Pr

This is the project's own description, as listed on CoinGecko. Treat it as a claim to check, not as evidence.

### 1.3 Supply

| Metric | Value | What This Means |
|---|---|---|
| Circulating Supply | 589,437,633 | Coins trading in the market today |
| Total Supply | 636,028,415 | Coins created so far, including locked ones |
| Maximum Supply | N/A | The hard cap, if there is one |
| Share Circulating | 92.7% | A low share means more supply can still reach the market |

> **Reading this table:** an asset with no maximum supply can keep issuing new coins. Check the project's documents for its issuance rules.

## Phase 1.5: Exchange Pool Maths

Main pool: orca on solana, found by contract address published by CoinGecko.

Most decentralised exchanges price a token with the constant product formula: x multiplied by y equals k. x is the number of tokens in the pool, y is the number of the paired token, and k stays fixed. When someone buys tokens out of the pool, x falls, so y has to rise to keep k the same, and the price goes up. Selling does the opposite.

| Variable | Value |
|---|---|
| Tokens in pool (x) | 188,170 |
| Paired tokens in pool (y) | 8,874,778 |
| k = x multiplied by y | 1,669,966,976,260 |
| Price change if 10% of x is bought out | 23.5% |

## Phase 2: Market Structure

### 2.1 Liquidity

| Metric | Value | What This Measures |
|---|---|---|
| Main DEX pool liquidity | $28,658,807 (R471,437,383) | Money in the main pool backing the price |
| 24h volume, main DEX pool | $97,779,157 (R1,608,467,139) | Trading in that one pool |
| 24h volume, all exchanges | $2,514,113,386 (R41,357,165,200) | Trading everywhere CoinGecko tracks |

### 2.1b Order-Book Depth on Large Exchanges

| Exchange | Pair | Selling Needed to Move the Price Down 2% |
|---|---|---|
| Coinbase Exchange | SOL/USD | $8,027,583 (R132,053,744) |
| Bitget | SOL/USDT | $5,763,269 (R94,805,770) |
| Crypto.com Exchange | SOL/USD | $5,454,335 (R89,723,803) |
| Kraken | SOL/USD | $5,430,795 (R89,336,581) |
| Binance | SOL/USDT | $5,208,178 (R85,674,523) |
| All counted markets | 21 markets | $52,823,880 (R868,952,823) |

> **Reading this table:** most trading in a blockchain's coin happens on centralised exchanges' order books, not in DEX pools. Depth is how many US Dollars of selling it takes to push the price down 2% on each book. Only large, established exchanges are counted, because smaller ones report depth that cannot be checked.

### 2.2 What a Large Sale Would Do

| Sale Size | Estimated Price Fall in the Main Pool |
|---|---|
| $50,000 (R822,500) | 0.50% |
| $100,000 (R1,645,000) | 1.00% |
| $500,000 (R8,225,000) | 4.86% |
| $1,000,000 (R16,450,000) | 9.38% |
| $5,000,000 (R82,250,000) | 36.24% |

> **Reading this table:** these figures assume the whole sale goes through the main DEX pool at once, with no fees and no arbitrage traders refilling it. Real trades are often split across exchanges, and many pools (Uniswap version 3, Orca) concentrate liquidity near the current price, which changes the real figure. Treat the numbers as a teaching estimate of pool depth, not a forecast.

## Phase 2.5: DeFi Activity

| Field | Value |
|---|---|
| Tracked as | chain |
| Name on DefiLlama | Solana |
| Total value locked (TVL) | $5,902,641,088 (R97,098,445,890) |
| How it was matched | native token of this chain |

> **Reading this table:** total value locked is the money deposited in a chain's or protocol's smart contracts. It shows how much the system is used, not what the token is worth.

## Phase 3: Derivatives

| Venue | Open Interest |
|---|---|
| OKX | $315,301,930 (R5,186,716,743) |
| Bitget | $425,277,374 (R6,995,812,801) |
| Gate | $402,569,708 (R6,622,271,695) |
| Hyperliquid | $574,224,709 (R9,445,996,464) |
| Total at these venues | $1,717,373,721 (R28,250,797,704) |

Source: OKX, Bitget, Gate and Hyperliquid public futures APIs (USDT-margined perpetuals). Venues not listed here are not counted, so the market-wide total is higher.

> **Reading this table:** open interest is the value of futures contracts not yet closed. When it is large compared with market cap, forced closures can make price moves bigger.

## Phase 4: Questions to Research Further

- Who holds the largest share of supply? Check the top holders on a block explorer.
- When do locked tokens unlock? Find the vesting schedule in the project's documents.
- What does the token do? Read the project's documents and check whether the token is needed to use the product.
- Who builds it? Check the public code repository for recent activity.
- What do regulators say? Search for the project's name on the FSCA and SEC websites.

## Risk Checks

> **How to read the risk checks:** each check compares one piece of public data with a teaching threshold chosen by this platform. "Flagged" means the data crossed the threshold. "Clear" means it did not. "No data" means the platform could not measure it, which is not the same as clear. The checks are not added up into a score, and none of them says whether to buy, sell or hold.

**0 flagged, 8 clear, 0 with no data.**

| Check | Result | Measured | Teaching threshold | What it means |
|---|---|---|---|---|
| Unusually high trading volume | Clear | 4.1% of market cap traded in 24 hours | More than 100% of market cap traded in 24 hours | When more than the whole market cap changes hands in a day, part of that volume is often wash trading (one party trading with itself to make a token look busy). |
| Thin market depth | Clear | $52,823,880 of selling moves the price 2% across 21 large-exchange markets | Less than $1,000,000 of selling moves the price 2% | Thin depth means a single large sale moves the price sharply (slippage). Deep books absorb large trades with little price change. |
| Large future supply (dilution) | Clear | Fully diluted value is 1.08 times market cap | Fully diluted value more than 3 times market cap | A large gap means many tokens are still to be released. Each release adds supply, and existing holders own a smaller share of the total afterwards. |
| Most supply not yet circulating | Clear | 92.7% of supply circulating | Less than 50% of supply circulating | A low float means the price today is set by a small part of the supply. The rest is held by teams, investors or treasuries and can reach the market later. |
| Not tracked by major data sites | Clear | Listed on CoinGecko | Absent from both CoinGecko and CoinMarketCap | Untracked tokens have less independent price and supply data, and scams are more common among them. A listing is not an endorsement either. |
| Large fall from all-time high | Clear | -64.1% from all-time high of $293 | Price more than 70% below its all-time high | A deep drawdown shows how volatile the token has been. It does not show whether the price will recover; many tokens never return to an earlier high. |
| Large price swing in 30 days | Clear | -6.3% over 30 days | Price moved more than 30% up or down in 30 days | Large swings in either direction mean the value of any holding can change quickly. |
| Heavy leveraged trading | Clear | Open interest is 2.8% of market cap | Open interest above 10% of market cap | Heavy leverage can turn a small price move into a large one, because forced closures (liquidations) trigger more buying or selling. |

### Not covered by these checks

No free, reliable source answers these, so the platform does not measure them. Check them yourself:

- **Token unlocks in the next 30 days.** Dates on which locked tokens become free to trade. Large unlocks often add selling pressure around the unlock date. Where to look: The project's own vesting documents, or a token-unlock tracker such as Tokenomist.
- **Supply held by a few wallets.** When a few wallets hold most of the supply, one decision by one holder can move the price. Where to look: A block explorer's top-holders list. Remember that exchange and contract wallets hold coins for many people.

## Sources and Limitations

| Source | What It Provides |
|---|---|
| DexScreener | Main exchange pool: price, liquidity, volume, pool balances |
| CoinGecko | Market cap, supply, price history, project description, exchange rate |
| CoinMarketCap | Whether the token is listed (listing check only) |
| Google News RSS | Recent headlines |
| DefiLlama | Total value locked and protocol category |
| CoinGecko exchange tickers | Order-book depth on large exchanges |
| OKX, Bitget, Gate, Hyperliquid | Open interest on perpetual futures (public APIs) |
| Coinglass | Open interest and liquidations, when an API key is set |
| Ultrasound.money | ETH burn data (ETH only) |

- The data is a snapshot taken on 19 October 2026 at 05:06 UTC. Markets move; check the sources for current values.
- The risk-check thresholds are teaching thresholds chosen by this platform, not industry standards.
- This is the data-only report. No AI wrote any part of it.
