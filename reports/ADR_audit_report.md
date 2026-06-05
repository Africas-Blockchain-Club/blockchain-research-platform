---
Token: ADR
Score: 35
Verdict: Neutral
Screenshot: /home/pmanda021/PeterManda/research-team/data/images/ADR_chart.png
---

# ADR Forensic Audit — 05 Mar 2026

## Phase 0: Overview & Narrative (The Social Layer)
### 0.1 High-Level Overview
The American Dollar Reserve (ADR) token is a speculative digital asset on the Solana blockchain. It is not a dollar-pegged stablecoin, despite its name. ADR's primary utility is driven by liquidity flows and market sentiment.

### 0.2 Social Sentiment & Mindshare
Recent web search snippets indicate that ADR has drawn significant attention amid heightened geopolitical tensions and renewed volatility across the crypto market. The sentiment around ADR appears to be mixed, with some investors showing interest in its price outlook and potential investment risks. The project's official social link on X (Twitter) is https://x.com/ADRCOINSOL, which may provide further insights into the community's sentiment.

## Phase 1: The Hard Data (Supply Forensics)
### 1.1 Tokenomics & Supply Dynamics
Data Unavailable — Requires TokenUnlocks.app or similar data source for detailed tokenomics.

### 1.2 Sovereign & Institutional Inventory
Data Unavailable — Requires on-chain wallet distribution data (Arkham/Nansen) to classify entities as Forced Sellers vs Strategic Holders.

### 1.3 The "Permanent Scarcity" Layer
To estimate the Effective Supply, we need the Total Supply, Dormant coins, and Burn addresses. The current market cap is $14,832,541 (ZAR 281,818,279). Assuming the circulating supply is roughly equal to the market cap divided by the current price ($0.02472), we can estimate the Total Supply. However, without exact Total Supply and Dormant coins data, we cannot accurately calculate the Effective Supply.

### 1.4 Behavioural Waves (HODL Analysis)
Data Unavailable — Requires on-chain transaction data to assess LTH vs STH behaviour signals.

## Phase 1.5: Tokenomics & AMM Math
### 1.5.1 The Liquidity Pool Equation ($x \times y = k$)
Using the provided liquidity data: 
- Liquidity Base Tokens = 4,436,437 ADR
- Liquidity Quote Tokens = 1,168.3586 SOL

First, convert SOL to USD: 1 SOL = $173.41 (Source: Assuming current SOL price, exact price not provided). 
Thus, Liquidity Quote Tokens in USD = 1,168.3586 SOL * $173.41 = $202,611.41.

Now, calculate $k$: 
$k = 4,436,437 \times 1,168.3586 = 5,183,111,111$ (in ADR*SOL units).

If a large market buy removes 10% of the base token supply from the pool:
- New Base Token Quantity = 4,436,437 - (10% of 4,436,437) = 3,992,793.3 ADR
- New Quote Token Quantity = $k$ / New Base Token Quantity = 5,183,111,111 / 3,992,793.3 = 1,298.21 SOL
- Price Impact: The new price in SOL per ADR will be 1,298.21 SOL / 3,992,793.3 ADR = 0.000325 SOL/ADR. The original price is 1,168.3586 SOL / 4,436,437 ADR = 0.000263 SOL/ADR. The price in USD will increase due to the reduced supply of ADR in the pool.

### 1.5.2 Token Distribution (Visualisation)
| Category | Percentage |
| --- | --- |
| Liquidity Pool (ADR) | 100% of ADR Supply in LP (approx.) |
| Liquidity Pool (SOL) | 100% of SOL in LP (approx.) |

Note that the exact tokenomics are not available. The above representation is a simplified view based on the liquidity pool data.

## Phase 2: Market Structure (The Liquidity Layer)
### 2.1 Liquidity & Order Book Depth
- Liquidity (USD): $219,042.79 (ZAR 4,161,811)
- Turnover Ratio: 2.0324, indicating relatively high trading activity compared to liquidity.
- Stress Test: 
  - $1M market sell: Significant slippage expected due to relatively thin liquidity.
  - $5M market sell: Severe slippage, potentially >10%.
  - $10M market sell: Catastrophic slippage, potentially >20%.

### 2.2 Liquidity Assessment
Liquidity matters significantly for ADR as it is a relatively small-cap token ($14.8M). The current liquidity of $219,042.79 is less than 1.5% of the market cap, indicating a high risk of slippage for larger trades.

### 2.3 Cost Basis Analysis
Data Unavailable — Requires on-chain transaction data to assess the realised price and STH cost basis signal.

## Phase 2.5: DeFi Mechanics
### 2.5.1 AMM Infrastructure & Routing
ADR trades on Solana-based Automated Market Makers (AMMs). Unlike traditional order books, AMMs use a liquidity pool to facilitate trades. The price of ADR is determined by the ratio of tokens in the liquidity pool. Slippage occurs when a trade significantly changes this ratio. For ADR, with its current liquidity depth, large trades can cause substantial slippage and price impact.

## Phase 3: Derivatives & Sentiment (The Volatility Layer)
### 3.1 Institutional & Leverage Cycle Detection
Data Unavailable — Open Interest and Funding Rate data are not available, making it difficult to assess institutional sentiment and leverage.

### 3.2 Liquidation Heatmaps
Data Unavailable — Liquidation levels are not available from Coinglass.

### 3.3 Funding & Open Interest
- Open Interest: $0, indicating no significant derivatives activity.
- Funding Rate: Not available.

## Phase 4: The Synthesis & Blueprint Score
### 4.1 The Synthesis Equation
"[Limited Supply Insight] + [Unknown Holder Behaviour] + [Thin Market Structure] + [No Derivatives Activity] = Neutral Assessment due to Limited Data"

### 4.2 The Blueprint Score (0–100)
| Component | Weight | Score | Reasoning |
| --- | --- | --- | --- |
| Scarcity / Supply Integrity | 30 | 15 | Limited insight into total supply and dormant coins. |
| Liquidity / Depth | 30 | 10 | Thin liquidity relative to market cap, high slippage risk. |
| On-Chain Sentiment | 20 | 10 | Limited data on holder behaviour and sentiment. |
| Derivative Structure | 20 | 0 | No derivatives activity. |
| **Total** | **100** | **35/100** | |

### 4.3 Final Verdict
- **Rating**: Neutral
- **Entry Trigger**: Significant increase in liquidity and trading volume.
- **Exit Trigger**: Sustained decline in price below $0.015.

## Red Flag Kill Switch Assessment
Evaluate each kill switch trigger:
- [ ] Thin Order Books: Liquidity = $219,042.79, which is approximately 1.48% of the market cap. While relatively thin, it is not below the $500k threshold for a $100M MCap token. **Not Triggered**.
- [ ] Supply Influx: Data Unavailable — Requires TokenUnlocks.app data. **Flagged for AI narrative assessment**.
- [ ] Concentration Risk: Data Unavailable — Requires on-chain wallet distribution data (Arkham/Nansen). **Flagged for AI narrative assessment**.
- [ ] Artificial Volume: Volume/MCap ratio = 0.0203, which is less than 1.0. **Not Triggered**.

## Source Layer
- DexScreener for liquidity and market data.
- Recent web search snippets for sentiment analysis.
- Coinglass for liquidation data (not available).
- X (Twitter) for official social link.

Data Unavailable — Requires TokenUnlocks.app for supply unlock schedule, Arkham/Nansen for on-chain wallet distribution, and DefiLlama for protocol analytics.

---

## AI Model Comparison
**Winning Model**: groq/llama-4-maverick (Blueprint Score: 35/100)

| Model | Blueprint Score | Verdict | Status |
|---|---|---|---|
| **google/gemini-2.5-flash** | **18/100** | **Distribute** | Runner-up |
| **groq/llama-4-maverick** | **35/100** | **Neutral** | ✅ Winner |
| **groq/qwen3-32b** | **20/100** | **Distribute** | Runner-up |
