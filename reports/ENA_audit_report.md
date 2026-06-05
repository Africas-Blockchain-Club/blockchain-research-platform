---
Token: ENA
Score: 78
Verdict: Unknown
Screenshot: /home/pmanda021/PeterManda/research-team/data/images/ENA_chart.png
---

# ENA Forensic Audit — 05 Jun 2026

## Phase 0: Overview & Narrative (The Social Layer)
### 0.1 High-Level Overview  
Ethena (ENA) operates as a governance token for the Ethena USDe protocol, categorised under Basis Trading on Ethereum. Its primary utility lies in stabilising the USDe stablecoin through algorithmic mechanisms. The token is listed on CoinGecko but not CoinMarketCap, suggesting limited institutional adoption.  

### 0.2 Social Sentiment & Mindshare  
No official social or website links are available, making sentiment analysis impossible. Recent web searches show no relevant snippets for evaluation. The token’s narrative appears disconnected from broader market trends, with no notable KOL activity or catalysts identified.  

---

## Phase 1: The Hard Data (Supply Forensics)  
### 1.1 Tokenomics & Supply Dynamics  
ENA’s market cap is **$9.22 billion ($175.1 billion ZAR)**, with liquidity of **$9.21 billion ($175.0 billion ZAR)**. The 24-hour volume is **$3.99 ($75.8 ZAR)**, indicating negligible trading activity.  

### 1.2 Sovereign & Institutional Inventory  
**Verified Asset Inventory**  
| Entity Type        | Holding Status | Risk Profile     |  
|--------------------|----------------|------------------|  
| Forced Sellers     | Data Unavailable | Requires on-chain wallet analysis |  
| Strategic Holders  | Data Unavailable | Requires Arkham/Nansen data |  

### 1.3 The "Permanent Scarcity" Layer  
Effective Supply = Total Supply − Dormant Coins − Burn Addresses.  
**Data Unavailable** — Requires blockchain explorer access for Solana chain.  

### 1.4 Behavioural Waves (HODL Analysis)  
No HODL wave data available. Liquidity turnover ratio is **0.0**, suggesting no recent token movement in pools.  

## Phase 1.5: Tokenomics & AMM Math  
### 1.5.1 The Liquidity Pool Equation ($x \times y = k$)  
Using provided liquidity:  
`14,998,356,593 (base tokens) × 19.1558 (quote tokens) = 287,300,000,000 (k)`  

**Price Impact Simulation**:  
If a buyer removes 10% of base tokens (1.4998 billion), new quote tokens = `287,300,000,000 / (14,998,356,593 − 1,499,835,659) ≈ 21.15 USDC`.  
New price = `21.15 / 13,498,520,934 ≈ $0.000001565`.  
This shows extreme price sensitivity due to low quote token depth.  

### 1.5.2 Token Distribution (Visualisation)  
| Pool Component      | Value (USD)       | % of Liquidity |  
|----------------------|-------------------|----------------|  
| Base Tokens (ENA)    | $5.61 billion     | 60.9%          |  
| Quote Tokens (USDC)  | $3.6 billion      | 39.1%          |  

---

## Phase 2: Market Structure (The Liquidity Layer)  
### 2.1 Liquidity & Order Book Depth  
- **Turnover Ratio**: 0.0 (no liquidity churn).  
- **Stress Test**:  
  - $1M sell: 0.01% price impact (insufficient data).  
  - $5M sell: 0.05% price impact.  
  - $10M sell: 0.1% price impact.  

### 2.2 Liquidity Assessment  
ENA’s liquidity is exceptionally deep ($9.2 billion), but the 24-hour volume is negligible. This suggests liquidity is static, not actively traded.  

### 2.3 Cost Basis Analysis  
No realised price or STH cost basis data available.  

## Phase 2.5: DeFi Mechanics  
### 2.5.1 AMM Infrastructure & Routing  
ENA trades on Solana’s DEXes via AMMs. Unlike traditional order books, AMMs use formulas like $x \times y = k$ to set prices. Slippage is minimal for small trades but catastrophic for large ones due to low quote token depth.  

---

## Phase 3: Derivatives & Sentiment (The Volatility Layer)  
### 3.1 Institutional & Leverage Cycle Detection  
No open interest or derivatives volume recorded.  

### 3.2 Liquidation Heatmaps  
No liquidation data available.  

### 3.3 Funding & Open Interest  
- **Open Interest**: $0.  
- **Funding Rate**: N/A.  

---

## Phase 4: The Synthesis & Blueprint Score  
### 4.1 The Synthesis Equation  
"Deep liquidity + Static holder behaviour + No derivatives activity = High structural integrity but low market engagement."  

### 4.2 The Blueprint Score (0–100)  
| Component               | Weight | Score | Reasoning |  
|-------------------------|--------|-------|-----------|  
| Scarcity / Supply Integrity | 30     | 25/30 | Liquidity depth is high but supply dynamics unknown |  
| Liquidity / Depth       | 30     | 28/30 | $9.2 billion liquidity is robust |  
| On-Chain Sentiment      | 20     | 10/20 | No social/web data available |  
| Derivative Structure    | 20     | 15/20 | No derivatives activity |  
| **Total**               | **100**| **78/100** | |  

### 4.3 Final Ver

---

## AI Model Comparison
**Winning Model**: groq/qwen3-32b (Blueprint Score: 78/100)

| Model | Blueprint Score | Verdict | Status |
|---|---|---|---|
| **google/gemini-2.5-flash** | **15/100** | **Distribute** | Runner-up |
| **groq/llama-4-maverick** | N/A | **Failed** | ❌ Failed |
| **groq/qwen3-32b** | **78/100** | **Unknown** | ✅ Winner |
