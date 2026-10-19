---
Token: BTC
Mode: data
Model: none
Generated: 2026-10-19T05:05:07.835031+00:00
Format: 3
---

# Bitcoin (BTC) Blockchain Research Report - 19 October 2026

> **Educational research, not financial advice.** This report explains what public data says about a blockchain and its native asset so that you can learn to read it. It does not recommend buying, selling or holding any crypto asset, and it does not take your circumstances into account. Africa's Blockchain Club is not an authorised financial services provider. Crypto assets are high risk and their price can fall to zero. Before you invest, speak to a financial services provider authorised by the Financial Sector Conduct Authority (FSCA).


## How to Read This Report

> This is the data-only version of the report: every number comes straight from the sources listed at the end, and no AI wrote any of it. Phase 0 explains the blockchain itself: what it is for, how it reaches agreement, and how its network is running right now. Phase 1 turns to its native asset: price, market size and supply. Phase 1.5 and Phase 2 show how its main exchange pool and the large exchanges' order books set the price. Phase 3 covers leveraged trading. The risk checks then compare the data with teaching thresholds. A check that says "No data" means the platform could not measure it, not that the risk is absent.

## Phase 0: The Blockchain

### 0.1 What It Is For

The first blockchain: a peer-to-peer system for sending value without a bank, now used mainly as a store of value and for settling large transfers.

| Question | Answer |
|---|---|
| Launched | January 2009 |
| How it reaches agreement | Proof of work. Miners compete to add each block by spending computing power (the SHA-256 algorithm); the chain with the most accumulated work is the valid one. |
| What can be built on it | Deliberately limited scripting (Bitcoin Script). Faster, cheaper payments run on layers built above it, such as the Lightning Network. |
| What the native asset does | BTC pays transaction fees and the block reward that pays miners. Supply is capped at 21 million; the new issuance per block halves roughly every four years. |
| Main uses today | Store of value, Settlement of large transfers, Payments over the Lightning Network, Collateral in other systems |

> **Reading this table:** the consensus method decides who can add blocks and what an attacker would need to control. The native asset's role tells you why anyone needs to hold it.

Check these facts at the source: https://bitcoin.org/bitcoin.pdf, https://developer.bitcoin.org/devguide/.

### 0.2 The Network Right Now

| Measure | Value | What It Means |
|---|---|---|
| Latest block | 972,106 | Bitcoin adds a block about every ten minutes. |
| Fee for next-block confirmation | 3 sat/vB | Satoshis (a hundred-millionth of a bitcoin) per virtual byte of transaction data. |
| Fee for confirmation within an hour | 1 sat/vB | What patient senders pay; the gap to the fastest fee shows how congested the network is. |
| Hash rate | 1,034 EH/s | Exahashes per second: the computing power securing the chain. More hash rate makes an attack costlier. |

Source: mempool.space public API. Read at the time of this report; the network keeps moving.

### 0.3 Building and Use

| Measure | Value | What It Means |
|---|---|---|
| Main client repository | [bitcoin/bitcoin](https://github.com/bitcoin/bitcoin) | The software most of the network's computers run |
| Commits in the last 4 weeks | 209 | Code changes accepted recently. Steady work is a sign of a maintained network |
| Last change | 19 October 2026 | When the repository last changed |
| Stars | 90,437 | Public interest from developers, not quality |
| Value locked in its apps (TVL) | $4,405,978,354 (R72,478,343,920) | Money deposited in apps built on this chain: a sign of real use |

> **Reading this table:** developer numbers come from one main repository on GitHub. Many chains develop across several repositories, some partly in private, so treat this as a partial view of the effort, not a measure of success.

### 0.4 Recent News Headlines

| Headline | Source | Published |
|---|---|---|
| Wall Street freaked out Friday, but VIX and bitcoin trades say the fear may fade Monday. | CoinDesk | Sun, 18 Oct 2026 23:24:37 GMT |
| Bitcoin Cash Is Up 18% This Month While Bitcoin Gained 6%. Can BCH Keep Outrunning BTC? | 24/7 Wall St. | Sun, 18 Oct 2026 21:17:00 GMT |
| AI Chip Bets Suffer $34M Liquidation Wipeout As Bitcoin, Ethereum Near Danger Zone Ahead Of Black Monday Fears | Yahoo Finance | Sun, 18 Oct 2026 16:52:52 GMT |
| Could Bitcoin Price Drop to $10,000? Bloomberg Analyst Gives Grim Warning | Yahoo Finance | Sun, 18 Oct 2026 14:39:53 GMT |
| Bitcoin’s path to $100,000 splits analysts as rate risks loom | CoinDesk | Sun, 18 Oct 2026 13:00:00 GMT |
| Saylor and Yusko's BTC Price Target, Bitmine's ETH Purchase and More: This Week in Crypto | TradingView | Sun, 18 Oct 2026 12:00:07 GMT |
| BTC Price Prediction: MACD Histogram Hits Zero as Bitcoin Stalls Below Key Averages With $84K Conditional | Blockchain News | Sun, 18 Oct 2026 07:08:20 GMT |
| Crypto Firms Launch Quantum Alliance as 6 Million Bitcoin Sit Exposed | Decrypt | Sat, 17 Oct 2026 16:01:03 GMT |

> **Reading this table:** headlines show what people are talking about, not what is true. Open the source and check who is making each claim.

## Phase 1: The Native Asset

### 1.1 Snapshot

| Name | Symbol | Price | 24h Change | 7d Change | 30d Change |
|---|---|---|---|---|---|
| Bitcoin | BTC | $82,646 (R1,359,527) | 1.14% | -1.68% | 2.04% |

| Market Cap | Fully Diluted Value | All-Time High | Change From All-Time High |
|---|---|---|---|
| $1,661,510,959,628 (R27,331,855,285,881) | $1,661,510,959,628 (R27,331,855,285,881) | $126,080 | -34.45% |

> **Reading this table:** market cap is price multiplied by circulating supply. Fully diluted value uses the maximum supply instead, so the gap between the two shows how many coins are still to come.

### 1.2 How the Project Describes Itself

> Bitcoin is the world's first decentralized cryptocurrency, created in 2009 by the pseudonymous Satoshi Nakamoto. It enables peer-to-peer electronic cash transactions without intermediaries like banks or governments, operating on a blockchain secured by Proof of Work mining and the SHA-256 cryptographic algorithm. With a fixed supply cap of 21 million coins and programmatic halvings every four years that reduce miner rewards, Bitcoin is designed as a deflationary digital asset often called "digital gold." Its value stems from solving the double-spending problem without trusted intermediaries,

This is the project's own description, as listed on CoinGecko. Treat it as a claim to check, not as evidence.

### 1.3 Supply

| Metric | Value | What This Means |
|---|---|---|
| Circulating Supply | 20,098,843 | Coins trading in the market today |
| Total Supply | 20,098,843 | Coins created so far, including locked ones |
| Maximum Supply | 21,000,000 | The hard cap, if there is one |
| Share Circulating | 95.7% | A low share means more supply can still reach the market |

> **Reading this table:** an asset with no maximum supply can keep issuing new coins. Check the project's documents for its issuance rules.

## Phase 1.5: Exchange Pool Maths

Main pool: raydium on solana, found by ticker search only; the contract could not be confirmed.

Most decentralised exchanges price a token with the constant product formula: x multiplied by y equals k. x is the number of tokens in the pool, y is the number of the paired token, and k stays fixed. When someone buys tokens out of the pool, x falls, so y has to rise to keep k the same, and the price goes up. Selling does the opposite.

| Variable | Value |
|---|---|
| Tokens in pool (x) | 99,997 |
| Paired tokens in pool (y) | 10 |
| k = x multiplied by y | 1,018,349 |
| Price change if 10% of x is bought out | 23.5% |

## Phase 2: Market Structure

### 2.1 Liquidity

| Metric | Value | What This Measures |
|---|---|---|
| Main DEX pool liquidity | $7,982,631,877 (R131,314,294,370) | Money in the main pool backing the price |
| 24h volume, main DEX pool | $58 (R949) | Trading in that one pool |
| 24h volume, all exchanges | $22,335,429,107 (R367,417,808,810) | Trading everywhere CoinGecko tracks |

### 2.1b Order-Book Depth on Large Exchanges

| Exchange | Pair | Selling Needed to Move the Price Down 2% |
|---|---|---|
| Gate | BTC/USDT | $28,458,045 (R468,134,842) |
| Binance | BTC/USDT | $22,191,295 (R365,046,811) |
| Coinbase Exchange | BTC/USD | $21,486,117 (R353,446,624) |
| Kraken | XBT/USD | $19,721,351 (R324,416,225) |
| OKX | BTC/USDT | $12,628,658 (R207,741,424) |
| All counted markets | 20 markets | $183,236,793 (R3,014,245,238) |

> **Reading this table:** most trading in a blockchain's coin happens on centralised exchanges' order books, not in DEX pools. Depth is how many US Dollars of selling it takes to push the price down 2% on each book. Only large, established exchanges are counted, because smaller ones report depth that cannot be checked.

### 2.2 What a Large Sale Would Do

| Sale Size | Estimated Price Fall in the Main Pool |
|---|---|
| $50,000 (R822,500) | 0.00% |
| $100,000 (R1,645,000) | 0.00% |
| $500,000 (R8,225,000) | 0.01% |
| $1,000,000 (R16,450,000) | 0.02% |
| $5,000,000 (R82,250,000) | 0.12% |

> **Reading this table:** these figures assume the whole sale goes through the main DEX pool at once, with no fees and no arbitrage traders refilling it. Real trades are often split across exchanges, and many pools (Uniswap version 3, Orca) concentrate liquidity near the current price, which changes the real figure. Treat the numbers as a teaching estimate of pool depth, not a forecast.

## Phase 2.5: DeFi Activity

| Field | Value |
|---|---|
| Tracked as | chain |
| Name on DefiLlama | Bitcoin |
| Total value locked (TVL) | $4,405,978,354 (R72,478,343,920) |
| How it was matched | native token of this chain |

> **Reading this table:** total value locked is the money deposited in a chain's or protocol's smart contracts. It shows how much the system is used, not what the token is worth.

## Phase 3: Derivatives

| Venue | Open Interest |
|---|---|
| OKX | $2,499,138,882 (R41,110,834,613) |
| Bitget | $2,826,946,430 (R46,503,268,771) |
| Gate | $2,160,960,882 (R35,547,806,511) |
| Hyperliquid | $3,265,665,440 (R53,720,196,496) |
| Total at these venues | $10,752,711,635 (R176,882,106,391) |

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
| Unusually high trading volume | Clear | 1.3% of market cap traded in 24 hours | More than 100% of market cap traded in 24 hours | When more than the whole market cap changes hands in a day, part of that volume is often wash trading (one party trading with itself to make a token look busy). |
| Thin market depth | Clear | $183,236,793 of selling moves the price 2% across 20 large-exchange markets | Less than $1,000,000 of selling moves the price 2% | Thin depth means a single large sale moves the price sharply (slippage). Deep books absorb large trades with little price change. |
| Large future supply (dilution) | Clear | Fully diluted value is 1.00 times market cap | Fully diluted value more than 3 times market cap | A large gap means many tokens are still to be released. Each release adds supply, and existing holders own a smaller share of the total afterwards. |
| Most supply not yet circulating | Clear | 95.7% of supply circulating | Less than 50% of supply circulating | A low float means the price today is set by a small part of the supply. The rest is held by teams, investors or treasuries and can reach the market later. |
| Not tracked by major data sites | Clear | Listed on CoinGecko | Absent from both CoinGecko and CoinMarketCap | Untracked tokens have less independent price and supply data, and scams are more common among them. A listing is not an endorsement either. |
| Large fall from all-time high | Clear | -34.4% from all-time high of $126,080 | Price more than 70% below its all-time high | A deep drawdown shows how volatile the token has been. It does not show whether the price will recover; many tokens never return to an earlier high. |
| Large price swing in 30 days | Clear | 2.0% over 30 days | Price moved more than 30% up or down in 30 days | Large swings in either direction mean the value of any holding can change quickly. |
| Heavy leveraged trading | Clear | Open interest is 0.6% of market cap | Open interest above 10% of market cap | Heavy leverage can turn a small price move into a large one, because forced closures (liquidations) trigger more buying or selling. |

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

- The data is a snapshot taken on 19 October 2026 at 05:05 UTC. Markets move; check the sources for current values.
- The risk-check thresholds are teaching thresholds chosen by this platform, not industry standards.
- This is the data-only report. No AI wrote any part of it.
