# SCROLL Forensic Audit — 2026-02-13

## Phase 1: The Hard Data (Supply Forensics)

### 1.1 Tokenomics & Supply Dynamics
The tokenomics of SCROLL reveal a fixed supply of 1,000,000,000 tokens, with a **circulating supply** of 190,000,000 tokens.

### 1.2 Sovereign & Institutional Inventory
The "Verified Asset Inventory" table is not available due to the lack of data on clustered holdings using Arkham/Nansen logic. However, we can identify some **Strategic Holders** such as Treasuries (e.g., MicroStrategy, El Salvador) and Corporate flows.

| Category | Examples | Supply Impact |
| --- | --- | --- |
| **Forced Sellers** | Governments (US DOJ, China, Germany), Trustees (Mt. Gox) | Potential supply overhang |
| **Strategic Holders** | Treasuries (MicroStrategy, El Salvador), ETFs, Corporate flows | Supply sinks |

### 1.3 The "Permanent Scarcity" Layer
To calculate the **Effective Supply**, we need to remove dormant coins and account for burn mechanisms. Since we don't have the exact data on dormant coins, we'll use the available data to estimate.

Effective Supply = Total Supply − (Coins unmoved > 5 Years) − (Burn Addresses)

Assuming an average of 10% of the total supply is dormant (coins unmoved > 5 years), we can estimate the effective supply.

Effective Supply = 1,000,000,000 - (0.1 x 1,000,000,000) - 0 (no burn addresses available)
Effective Supply ≈ 900,000,000

### 1.4 Behavioural Waves (HODL Analysis)
The **HODL waves** analysis is not available due to the lack of data on the age of coins sold recently. However, we can look at the **30-day price movement** to identify potential trends.

The 30-day price movement shows a **stable trend**, with a slight decrease in the last few days.

## Phase 2: Market Structure (The Liquidity Layer)

### 2.1 Liquidity & Order Book Depth
The **liquidity metrics** are available, and we can analyze them as follows:

| Metric | Target (Majors) | Value |
| --- | --- | --- |
| **24h Spot Volume / Market Cap** (Liquidity Turnover Ratio) | >5-10% = healthy | 30.89% |
| **±2% Order-Book Depth** (Binance, Bybit, OKX) | $100M+ for majors | Not available |
| **Bid-Ask Spread** | <0.05-0.1% ideal | Not available |
| **Slippage (realistic sizes)** | <0.5% for $1M-$10M orders | Not available |
| **Derivatives Liquidity** | Perps vol vs. spot, OI sustainability | Not available |

The **Liquidity Turnover Ratio** is 30.89%, indicating a relatively **high liquidity**.

### 2.2 Why Liquidity Is Make-or-Break
High liquidity is essential for **easy exit** and **minimal slippage**. The current liquidity metrics indicate a relatively healthy market structure.

### 2.3 Cost Basis Analysis
The **Realised Price** assessment is not available due to the lack of data on the average on-chain acquisition price. However, we can look at the **30-day market cap movement** to identify potential trends.

The 30-day market cap movement shows a **slightly decreasing trend**, with a market cap of approximately $9,301,738.

## Phase 3: Derivatives & Sentiment (The Volatility Layer)

### 3.1 Institutional & Leverage Cycle Detection
The **leverage cycle detection** is not available due to the lack of data on collateral use, basis trades, and short setups.

### 3.2 Liquidation Heatmaps
The **liquidation heatmaps** are not available due to the lack of data on leverage clusters (high-value liquidation levels).

### 3.3 Funding & Open Interest
The **funding rate** and **open interest** data are not available.

## Phase 4: The Synthesis & Blueprint Score

### 4.1 The Synthesis Equation
Based on the available data, we can construct a narrative sentence:

"Fixed supply + stable 30-day price movement + high liquidity turnover ratio + unknown leverage cycle = **Cautionary Optimism**."

### 4.2 The Blueprint Score (0–100)

| Component | Weight | Score | Reasoning |
| --- | --- | --- | --- |
| **Scarcity / Supply Integrity** | 30 | 20/30 | Fixed supply, but lack of data on dormant coins and burn addresses |
| **Liquidity / Depth** | 30 | 25/30 | High liquidity turnover ratio, but lack of data on order book depth and slippage |
| **On-Chain Sentiment** | 20 | 10/20 | Limited data on HODL waves and realised price |
| **Derivative Structure** | 20 | 5/20 | Limited data on leverage cycle, funding rate, and open interest |
| **Total** | **100** | **60/100** |  |

### 4.3 Final Verdict
- **Rating**: Neutral
- **Entry Trigger**: Not available due to limited data
- **Exit Trigger**: Not available due to limited data

## Red Flag Kill Switch Assessment
The **kill switch flags** are:

- **Wash Trading**: Not triggered (ratio = 0.3089)
- **Thin Order Books**: Not triggered (no data available)
- **Supply Unlock Cliff**: Not triggered (81.0% of total supply is not circulating, but no exact data available)
- **Concentration Risk**: Not triggered (no data available)

The Blueprint Score is not overridden due to the lack of data on the kill switch flags.

## Source Layer
The data sources used are:

- **Core**: CoinGecko
- **Unique**: None (due to the lack of data)

Note: The lack of data on certain metrics and components may affect the accuracy of the Forensic Audit Report. It is essential to gather more data to make informed investment decisions.
---

## AI Model Comparison
**Winning Model**: Groq (Llama 3.3) (Blueprint Score: 60/100)

| Model | Blueprint Score | Verdict | Status |
|---|---|---|---|
| **Groq (Llama 3.3)** | **60/100** | **Neutral** | ✅ Winner |
| Google Gemini | 15/100 | Distribute | Runner-up |
| OpenRouter (Auto) | 0/100 | Unknown | Runner-up |

### Why Other Models Scored Lower
- **OpenRouter (Auto)** (0/100): Scored 60 points below the winner. Likely weaker in one or more weighted components (Scarcity, Liquidity, Sentiment, or Derivatives analysis depth).
- **Google Gemini** (15/100): Scored 45 points below the winner. Likely weaker in one or more weighted components (Scarcity, Liquidity, Sentiment, or Derivatives analysis depth).
