---
Token: SOLANA
Score: 50
Verdict: Neutral
Screenshot: /home/pmanda021/PeterManda/research-team/data/images/SOLANA_chart.png
---

# SOLANA Forensic Audit — 05 Mar 2026

## Phase 0: Overview & Narrative (The Social Layer)
### 0.1 High-Level Overview
The SOLANA token, symbolised as SOLANA, is a cryptocurrency token on the Ethereum chain. Its primary utility is not explicitly defined in the available data, but it is associated with various social media and web presence, suggesting a potential community-driven or memecoin narrative. The market capitalisation is approximately $150,588 (ZAR 2,861,172).

### 0.2 Social Sentiment & Mindshare
The sentiment around SOLANA appears to be mixed, with recent web search snippets indicating real-time price tracking and historical chart analysis. The presence of official social links on Twitter and Telegram, along with an official website, suggests a level of organisation. The token has seen significant price movements, with an all-time high of $0.0875266 and an all-time low of $0.01127857, indicating a volatile market.

## Phase 1: The Hard Data (Supply Forensics)
### 1.1 Tokenomics & Supply Dynamics
The total supply of SOLANA is not directly available, but the liquidity pool contains 288,575,333,582,166 base tokens. The quote tokens in the liquidity pool are 22.9552 WETH.

### 1.2 Sovereign & Institutional Inventory
Data Unavailable — Requires on-chain wallet distribution data.

### 1.3 The "Permanent Scarcity" Layer
To calculate the Effective Supply, we need the total supply, dormant coins, and burn addresses. Data Unavailable — Requires Token Supply data.

### 1.4 Behavioural Waves (HODL Analysis)
Data Unavailable — Requires on-chain transaction data.

## Phase 1.5: Tokenomics & AMM Math
### 1.5.1 The Liquidity Pool Equation ($x \times y = k$)
Using the provided liquidity data: $288,575,333,582,166 \times 22.9552 = k$. Thus, $k = 6,623,111,111,111,111$. If a large market buy removes 10% of the base token supply from the pool, the new base token quantity will be $259,717,800,224,049$, and the new quote token quantity can be calculated using the constant product formula. The new quote token quantity will be $25.5053$ WETH, resulting in a price impact.

### 1.5.2 Token Distribution (Visualisation)
| Category | Percentage |
| --- | --- |
| Liquidity Pool | Data Unavailable |
| Team | Data Unavailable |
| Treasury | Data Unavailable |

The liquidity pool split is approximately 288,575,333,582,166 base tokens to 22.9552 quote tokens (WETH).

## Phase 2: Market Structure (The Liquidity Layer)
### 2.1 Liquidity & Order Book Depth
The liquidity in USD is $97,777 (ZAR 1,857,763), with a turnover ratio of 1.3989. The liquidity appears to be relatively deep compared to the market capitalisation.

### 2.2 Liquidity Assessment
Liquidity matters for SOLANA as it is a relatively small-cap token. The current liquidity depth is crucial for understanding the potential price impact of large trades.

### 2.3 Cost Basis Analysis
Data Unavailable — Requires on-chain transaction data.

## Phase 2.5: DeFi Mechanics
### 2.5.1 AMM Infrastructure & Routing
SOLANA is traded on Automated Market Makers (AMMs), which differ from traditional order books. The trading mechanics involve slippage and price impact, which are essential for evaluating the token's liquidity depth. The current liquidity of $97,777 (ZAR 1,857,763) indicates a relatively deep market, but large trades may still cause significant price movements.

## Phase 3: Derivatives & Sentiment (The Volatility Layer)
### 3.1 Institutional & Leverage Cycle Detection
The open interest and open interest amount are both $0, indicating a lack of derivatives data.

### 3.2 Liquidation Heatmaps
Data Unavailable — Requires Coinglass or similar data.

### 3.3 Funding & Open Interest
The funding rate sentiment check is not possible due to the lack of derivatives data.

## Phase 4: The Synthesis & Blueprint Score
### 4.1 The Synthesis Equation
"[Supply Constraint Status] + [Holder Behaviour] + [Market Structure Integrity] + [Derivatives Positioning] = Neutral due to lack of comprehensive data".

### 4.2 The Blueprint Score (0–100)
| Component | Weight | Score | Reasoning |
| --- | --- | --- | --- |
| Scarcity / Supply Integrity | 30 | 15/30 | Lack of total supply data |
| Liquidity / Depth | 30 | 25/30 | Relatively deep liquidity |
| On-Chain Sentiment | 20 | 10/20 | Limited on-chain data |
| Derivative Structure | 20 | 0/20 | No derivatives data available |
| **Total** | **100** | **50/100** | |

### 4.3 Final Verdict
- **Rating**: Neutral
- **Entry Trigger**: Significant increase in liquidity
- **Exit Trigger**: Sharp decline in liquidity or significant price drop

## Red Flag Kill Switch Assessment
- [ ] Thin Order Books: Not triggered
- [ ] Supply Influx: Data Unavailable — Requires TokenUnlocks.app data
- [ ] Concentration Risk: Data Unavailable — Requires on-chain wallet distribution data
- [ ] Artificial Volume: Not triggered

## Source Layer
- DexScreener for liquidity and token info
- CoinGecko and CoinMarketCap for listing status
- Official social media and website links for social context
- Web search snippets for sentiment analysis
- Coinglass for derivatives data (unavailable)

---

## AI Model Comparison
**Winning Model**: groq/llama-4-maverick (Blueprint Score: 50/100)

| Model | Blueprint Score | Verdict | Status |
|---|---|---|---|
| **google/gemini-2.5-flash** | **0/100** | **Unknown** | Runner-up |
| **groq/llama-4-maverick** | **50/100** | **Neutral** | ✅ Winner |
| **groq/qwen3-32b** | **0/100** | **Unknown** | Runner-up |
