---
Token: ETH
Mode: data
Model: none
Generated: 2026-10-19T05:05:29.790445+00:00
Format: 3
---

# Ethereum (ETH) Blockchain Research Report - 19 October 2026

> **Educational research, not financial advice.** This report explains what public data says about a blockchain and its native asset so that you can learn to read it. It does not recommend buying, selling or holding any crypto asset, and it does not take your circumstances into account. Africa's Blockchain Club is not an authorised financial services provider. Crypto assets are high risk and their price can fall to zero. Before you invest, speak to a financial services provider authorised by the Financial Sector Conduct Authority (FSCA).


## How to Read This Report

> This is the data-only version of the report: every number comes straight from the sources listed at the end, and no AI wrote any of it. Phase 0 explains the blockchain itself: what it is for, how it reaches agreement, and how its network is running right now. Phase 1 turns to its native asset: price, market size and supply. Phase 1.5 and Phase 2 show how its main exchange pool and the large exchanges' order books set the price. Phase 3 covers leveraged trading. The risk checks then compare the data with teaching thresholds. A check that says "No data" means the platform could not measure it, not that the risk is absent.

## Phase 0: The Blockchain

### 0.1 What It Is For

A general-purpose blockchain for programs (smart contracts), and the settlement layer that many layer 2 networks post their transactions to.

| Question | Answer |
|---|---|
| Launched | July 2015 |
| How it reaches agreement | Proof of stake since September 2022 (the Merge). Validators lock 32 ETH each, propose and attest to blocks in 12-second slots, and lose stake if they cheat. |
| What can be built on it | Full smart contracts on the Ethereum Virtual Machine (EVM), usually written in Solidity. Many other chains copy the EVM so the same code runs there. |
| What the native asset does | ETH pays for computation (gas) and is the stake that secures the network. There is no fixed supply cap; since August 2021 part of every fee is burned (EIP-1559), which offsets new issuance. |
| Main uses today | Decentralised finance (DeFi), Stablecoins, Tokens and NFTs, Settlement for layer 2 rollups |

> **Reading this table:** the consensus method decides who can add blocks and what an attacker would need to control. The native asset's role tells you why anyone needs to hold it.

Check these facts at the source: https://ethereum.org/en/developers/docs/, https://ethereum.org/en/roadmap/merge/.

### 0.2 The Network Right Now

| Measure | Value | What It Means |
|---|---|---|
| Latest block | 26,224,417 | How many blocks the chain has produced; it should keep rising. |
| Average block time | 12.24 seconds | Measured over the last 100 blocks: how often new transactions are confirmed. |
| Gas price | 0.0434 gwei | The price per unit of computation (1 gwei is a billionth of the native coin). Higher means busier or more expensive. |
| Transactions in the latest block | 151 | A rough sign of how busy the chain is right now. |

Source: Public JSON-RPC endpoint (https://ethereum-rpc.publicnode.com). Read at the time of this report; the network keeps moving.

### 0.3 Building and Use

| Measure | Value | What It Means |
|---|---|---|
| Main client repository | [ethereum/go-ethereum](https://github.com/ethereum/go-ethereum) | The software most of the network's computers run |
| Commits in the last 4 weeks | 85 | Code changes accepted recently. Steady work is a sign of a maintained network |
| Last change | 19 October 2026 | When the repository last changed |
| Stars | 51,412 | Public interest from developers, not quality |
| Value locked in its apps (TVL) | $49,858,149,661 (R820,166,561,927) | Money deposited in apps built on this chain: a sign of real use |

> **Reading this table:** developer numbers come from one main repository on GitHub. Many chains develop across several repositories, some partly in private, so treat this as a partial view of the effort, not a measure of success.

### 0.4 Recent News Headlines

| Headline | Source | Published |
|---|---|---|
| Top 3 Price Predictions: Bitcoin, Ethereum, Ripple – BTC rebounds to $82,500 as ETH and XRP hold support | FXStreet | Mon, 19 Oct 2026 03:18:24 GMT |
| Ethereum Is Testing Blocks Over 3 Times Bigger. Could That Help ETH Catch Up With Solana? | Yahoo Finance | Sun, 18 Oct 2026 20:20:24 GMT |
| AI Chip Bets Suffer $34M Liquidation Wipeout As Bitcoin, Ethereum Near Danger Zone Ahead Of Black Monday Fears | Yahoo Finance | Sun, 18 Oct 2026 16:52:52 GMT |
| ETH Sits 'In The Middle Of Nothing' Heading Into The Back Half Of A Red October | Stocktwits | Sun, 18 Oct 2026 15:09:00 GMT |
| Saylor and Yusko's BTC Price Target, Bitmine's ETH Purchase and More: This Week in Crypto | TradingView | Sun, 18 Oct 2026 12:00:07 GMT |
| Justin Sun sells most of his ETH and moves into US stocks | TradingView | Sun, 18 Oct 2026 08:36:49 GMT |
| Wall Street's Biggest Settlement Firm Is Lining Up Stellar for 2027. Is XLM a Better Buy Than Ethereum? | 24/7 Wall St. | Sat, 17 Oct 2026 21:01:00 GMT |
| Not Bitcoin. Not Ethereum. These 4 Cryptocurrencies Could Be Worth Holding for the Next 5 Years. | The Motley Fool | Fri, 16 Oct 2026 11:45:00 GMT |

> **Reading this table:** headlines show what people are talking about, not what is true. Open the source and check who is making each claim.

## Phase 1: The Native Asset

### 1.1 Snapshot

| Name | Symbol | Price | 24h Change | 7d Change | 30d Change |
|---|---|---|---|---|---|
| Ethereum | ETH | $2,421 (R39,823) | 0.36% | -5.59% | -7.56% |

| Market Cap | Fully Diluted Value | All-Time High | Change From All-Time High |
|---|---|---|---|
| $295,740,004,923 (R4,864,923,080,983) | $295,740,004,923 (R4,864,923,080,983) | $4,946 | -51.06% |

> **Reading this table:** market cap is price multiplied by circulating supply. Fully diluted value uses the maximum supply instead, so the gap between the two shows how many coins are still to come.

### 1.2 How the Project Describes Itself

> Ethereum is a global, open-source platform for decentralized applications. In other words, it is a decentralized blockchain platform that enables developers to build and deploy smart contracts and applications without central authority control. Unlike Bitcoin, which primarily functions as digital currency, Ethereum operates as a programmable global computer where developers can create any type of decentralized service. The platform hosts over $14 billion in DeFi applications with hundreds of thousands of active users across financial protocols, NFT marketplaces, and gaming platforms. Its tra

This is the project's own description, as listed on CoinGecko. Treat it as a claim to check, not as evidence.

### 1.3 Supply

| Metric | Value | What This Means |
|---|---|---|
| Circulating Supply | 122,148,378 | Coins trading in the market today |
| Total Supply | 122,148,378 | Coins created so far, including locked ones |
| Maximum Supply | N/A | The hard cap, if there is one |
| Share Circulating | 100.0% | A low share means more supply can still reach the market |

> **Reading this table:** an asset with no maximum supply can keep issuing new coins. Check the project's documents for its issuance rules.

## Phase 1.5: Exchange Pool Maths

Main pool: uniswap on ethereum, found by contract address published by CoinGecko.

Most decentralised exchanges price a token with the constant product formula: x multiplied by y equals k. x is the number of tokens in the pool, y is the number of the paired token, and k stays fixed. When someone buys tokens out of the pool, x falls, so y has to rise to keep k the same, and the price goes up. Selling does the opposite.

| Variable | Value |
|---|---|
| Tokens in pool (x) | 27,124 |
| Paired tokens in pool (y) | 29,119,417 |
| k = x multiplied by y | 789,835,066,708 |
| Price change if 10% of x is bought out | 23.5% |

## Phase 2: Market Structure

### 2.1 Liquidity

| Metric | Value | What This Measures |
|---|---|---|
| Main DEX pool liquidity | $94,959,551 (R1,562,084,615) | Money in the main pool backing the price |
| 24h volume, main DEX pool | $20,958,606 (R344,769,063) | Trading in that one pool |
| 24h volume, all exchanges | $9,020,486,468 (R148,387,002,399) | Trading everywhere CoinGecko tracks |

### 2.1b Order-Book Depth on Large Exchanges

| Exchange | Pair | Selling Needed to Move the Price Down 2% |
|---|---|---|
| Kraken | ETH/USD | $13,050,483 (R214,680,447) |
| Binance | ETH/USDT | $11,167,343 (R183,702,800) |
| Coinbase Exchange | ETH/USD | $10,426,021 (R171,508,043) |
| OKX | ETH/USDT | $7,331,881 (R120,609,436) |
| Gate | ETH/USDT | $7,101,038 (R116,812,080) |
| All counted markets | 19 markets | $78,140,094 (R1,285,404,549) |

> **Reading this table:** most trading in a blockchain's coin happens on centralised exchanges' order books, not in DEX pools. Depth is how many US Dollars of selling it takes to push the price down 2% on each book. Only large, established exchanges are counted, because smaller ones report depth that cannot be checked.

### 2.2 What a Large Sale Would Do

| Sale Size | Estimated Price Fall in the Main Pool |
|---|---|
| $50,000 (R822,500) | 0.15% |
| $100,000 (R1,645,000) | 0.30% |
| $500,000 (R8,225,000) | 1.51% |
| $1,000,000 (R16,450,000) | 2.98% |
| $5,000,000 (R82,250,000) | 13.65% |

> **Reading this table:** these figures assume the whole sale goes through the main DEX pool at once, with no fees and no arbitrage traders refilling it. Real trades are often split across exchanges, and many pools (Uniswap version 3, Orca) concentrate liquidity near the current price, which changes the real figure. Treat the numbers as a teaching estimate of pool depth, not a forecast.

## Phase 2.5: DeFi Activity

| Field | Value |
|---|---|
| Tracked as | chain |
| Name on DefiLlama | Ethereum |
| Total value locked (TVL) | $49,858,149,661 (R820,166,561,927) |
| How it was matched | native token of this chain |

> **Reading this table:** total value locked is the money deposited in a chain's or protocol's smart contracts. It shows how much the system is used, not what the token is worth.

## Phase 3: Derivatives

| Venue | Open Interest |
|---|---|
| OKX | $1,433,290,483 (R23,577,628,441) |
| Bitget | $1,844,562,866 (R30,343,059,149) |
| Gate | $946,361,190 (R15,567,641,583) |
| Hyperliquid | $2,570,382,863 (R42,282,798,104) |
| Total at these venues | $6,794,597,403 (R111,771,127,277) |

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
| Unusually high trading volume | Clear | 3.1% of market cap traded in 24 hours | More than 100% of market cap traded in 24 hours | When more than the whole market cap changes hands in a day, part of that volume is often wash trading (one party trading with itself to make a token look busy). |
| Thin market depth | Clear | $78,140,094 of selling moves the price 2% across 19 large-exchange markets | Less than $1,000,000 of selling moves the price 2% | Thin depth means a single large sale moves the price sharply (slippage). Deep books absorb large trades with little price change. |
| Large future supply (dilution) | Clear | Fully diluted value is 1.00 times market cap | Fully diluted value more than 3 times market cap | A large gap means many tokens are still to be released. Each release adds supply, and existing holders own a smaller share of the total afterwards. |
| Most supply not yet circulating | Clear | 100.0% of supply circulating | Less than 50% of supply circulating | A low float means the price today is set by a small part of the supply. The rest is held by teams, investors or treasuries and can reach the market later. |
| Not tracked by major data sites | Clear | Listed on CoinGecko | Absent from both CoinGecko and CoinMarketCap | Untracked tokens have less independent price and supply data, and scams are more common among them. A listing is not an endorsement either. |
| Large fall from all-time high | Clear | -51.1% from all-time high of $4,946 | Price more than 70% below its all-time high | A deep drawdown shows how volatile the token has been. It does not show whether the price will recover; many tokens never return to an earlier high. |
| Large price swing in 30 days | Clear | -7.6% over 30 days | Price moved more than 30% up or down in 30 days | Large swings in either direction mean the value of any holding can change quickly. |
| Heavy leveraged trading | Clear | Open interest is 2.3% of market cap | Open interest above 10% of market cap | Heavy leverage can turn a small price move into a large one, because forced closures (liquidations) trigger more buying or selling. |

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
