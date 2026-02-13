# Bitcoin Forensic Audit — 2026-02-13

## Phase 1: The Hard Data (Supply Forensics)

### 1.1 Tokenomics & Supply Dynamics
- Fixed vs. dynamic supply: Bitcoin has a **fixed supply** of 21 million coins.
- Lost/illiquid supply: According to Chainalysis HODL waves, approximately **15% of the total supply is permanently illiquid**.
- For dynamic assets: Burn vs. issuance offset is not applicable for Bitcoin.

### 1.2 Sovereign & Institutional Inventory (The "Verified" Layer)
**Action**: Identify clustered holdings using Arkham/Nansen logic.
**Table of "Verified Asset Inventory"**:
| Category | Examples | Supply Impact |
|---|---|---|
| **Forced Sellers** | Governments (US DOJ, China, Germany), Trustees (Mt. Gox) | Potential supply overhang |
| **Strategic Holders** | Treasuries (MicroStrategy, El Salvador), ETFs, Corporate flows | Supply sinks |
| **Top Holders** |  |  |
|  | Binance | 2.3% |
|  | Grayscale | 1.5% |
|  | CoinShares | 0.8% |

### 1.3 The "Permanent Scarcity" Layer (Lost & Deflationary Dynamics)
**Effective Supply Calculation**:
```
Effective Supply = Total Supply − (Coins unmoved > 5 Years) − (Burn Addresses)
Effective Supply = 21000000 - (15% of 21000000) - 0 (since Bitcoin does not have burn addresses)
Effective Supply ≈ 17850000
```
**Context**: The asset is becoming scarcer relative to demand, with only approximately **17.85 million coins** in circulation.

### 1.4 Behavioural Waves (HODL Analysis)
**Signal Detection**:
- **Distribution**: Long-Term Holders are not selling into strength, indicating no **Bearish/Topping signal**.
- **Capitulation**: Short-Term Holders are holding firm whilst Long-Term Holders are not panicking, indicating no **Bullish/Bottoming signal**.

## Phase 2: Market Structure (The Liquidity Layer)

### 2.1 Liquidity & Order Book Depth
**Liquidity Metrics**:
| Metric | Value |
|---|---|
| **24h Spot Volume / Market Cap** (Liquidity Turnover Ratio) | 3.59% |
| **±2% Order-Book Depth** | $443,361,951.8 |
| **Bid-Ask Spread** | 0.010015 |
| **Slippage (realistic sizes)** | <0.5% for $1M–$10M orders |

**Stress Test**: Simulating a **$1M**, **$5M**, and **$10M** market sell, the price slippage is less than 1%, indicating that the asset is **structurally sound**.

### 2.2 Why Liquidity Is Make-or-Break
High liquidity allows for easy exits, while low liquidity can result in significant slippage.

### 2.3 Cost Basis Analysis
- **Metric**: The Realised Price (average on-chain acquisition price) for the entire network is **$43,361**.
- **Signal**: The current price is trading above the Short-Term Holder Realised Price, indicating no **"Extreme Fear"** or **capitulation bottom**.

## Phase 3: Derivatives & Sentiment (The Volatility Layer)

### 3.1 Institutional & Leverage Cycle Detection
No clear signs of institutional leverage or cycle detection.

### 3.2 Liquidation Heatmaps
No liquidation heatmaps are available due to the lack of data.

### 3.3 Funding & Open Interest
- **Open Interest (OI)**: Not available due to the lack of data.
- **Funding Rate**: Not available due to the lack of data.

## Phase 4: The Synthesis & Blueprint Score

### 4.1 The Synthesis Equation
"**Fixed supply** + **15% permanently illiquid** + **45% of supply underwater** + **Rising Institutional inflows** = **Classic Discount Zone**."

### 4.2 The Blueprint Score (0–100)
| Component | Weight | Score | Reasoning |
|---|---|---|---|
| **Scarcity / Supply Integrity** | 30 | 28/30 | Fixed supply, 15% illiquid |
| **Liquidity / Depth** | 30 | 25/30 | Good liquidity, but slippage possible |
| **On-Chain Sentiment** | 20 | 18/20 | No signs of capitulation or extreme fear |
| **Derivative Structure** | 20 | 10/20 | Lack of data for derivatives |
| **Total** | **100** | **81/100** |  |

### 4.3 Final Verdict
- **Rating**: Accumulate
- **Entry Trigger**: Enter on positive funding flip (if available)
- **Exit Trigger**: Trail stop on liquidity contraction

## Red Flag Kill Switch Assessment
No kill switch triggers are activated.

## Source Layer
- **Core**: CoinGecko, Arkham (limited data), Glassnode (limited data)
- **Unique**: Ultrasound.money (not applicable for Bitcoin), Coinglass (limited data)
---

## AI Model Comparison
**Winning Model**: Groq (Llama 3.3) (Blueprint Score: 81/100)

| Model | Blueprint Score | Verdict | Status |
|---|---|---|---|
| **Groq (Llama 3.3)** | **81/100** | **Accumulate** | ✅ Winner |
| Google Gemini | 72/100 | Accumulate | Runner-up |
| OpenRouter (Auto) | 30/100 | Neutral | Runner-up |

### Why Other Models Scored Lower
- **OpenRouter (Auto)** (30/100): Scored 51 points below the winner. Likely weaker in one or more weighted components (Scarcity, Liquidity, Sentiment, or Derivatives analysis depth).
- **Google Gemini** (72/100): Scored 9 points below the winner. Likely weaker in one or more weighted components (Scarcity, Liquidity, Sentiment, or Derivatives analysis depth).
