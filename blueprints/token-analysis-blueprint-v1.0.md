# The Token Audit & Blueprint Protocol
**Liquidity-First Forensic Audit for Any Cryptocurrency Token**

**Objective**: Generate a forensic data science report on **[TOKEN NAME]** that synthesises on-chain supply dynamics, market structure liquidity, and derivative positioning.

**Output Standard**: The report must provide a calculated **"Blueprint Score" (0–100)** and actionable synthesis, matching the depth and clarity of high-level institutional crypto research.

**Purpose**: Repeatable framework for data-driven investment decisions. Focus on realising profits (liquidity = you can actually take them).

---

## Phase 1: The Hard Data (Supply Forensics)

**Goal**: Determine the "True" Circulating Supply versus the "Theoretical" Supply.

### 1.1 Tokenomics & Supply Dynamics
- Fixed vs. dynamic supply.
- Lost/illiquid supply (Glassnode HODL waves, Chainalysis estimates).
- For dynamic assets: Burn vs. issuance offset (ultrasound.money style — deflationary = bullish scarcity).

### 1.2 Sovereign & Institutional Inventory (The "Verified" Layer)
**Action**: Identify clustered holdings using Arkham/Nansen logic.

**Differentiation** — you must distinguish between:
| Category | Examples | Supply Impact |
|---|---|---|
| **Forced Sellers** | Governments (US DOJ, China, Germany), Trustees (Mt. Gox) | Potential supply overhang |
| **Strategic Holders** | Treasuries (MicroStrategy, El Salvador), ETFs, Corporate flows | Supply sinks |

- Holdings concentration (% owned by entities).
- ETF/corporate flows.
- Institutional/government treasuries (Arkham Intelligence, CoinGecko Treasuries).

**Output**: Create a table of "Verified Asset Inventory" comprising the top labelled entities.

### 1.3 The "Permanent Scarcity" Layer (Lost & Deflationary Dynamics)
**Action**: Calculate "Effective Supply" by removing dormant coins and accounting for burn mechanisms.

**Formula**:
```
Effective Supply = Total Supply − (Coins unmoved > 5 Years [or >10 for mature chains]) − (Burn Addresses)
```

- **Ethereum Specifics**: For ETH analysis, explicitly consult [ultrasound.money](https://ultrasound.money/) to verify the real-time burn rate vis-à-vis issuance. Determine if the asset is currently net inflationary or deflationary (supply crunch).
- **Context**: Compare this "Illiquid Supply" metric to the current issuance rate. Is the asset becoming scarcer relative to demand?

### 1.4 Behavioural Waves (HODL Analysis)
**Action**: Analyse the age of coins sold recently (e.g., Realised Cap HODL Waves).

**Signal Detection**:
- **Distribution**: Are Long-Term Holders (LTH) selling into strength? → *Bearish/Topping signal*.
- **Capitulation**: Are LTHs holding firm whilst Short-Term Holders panic sell? → *Bullish/Bottoming signal*.

---

## Phase 2: Market Structure (The Liquidity Layer)

**Goal**: Assess if the market can support an exit without slippage.

> **Principle**: "Profit is theoretical; Liquidity is realised."

### 2.1 Liquidity & Order Book Depth
Metrics to track (live via APIs or CoinGecko/Coinglass/Amberdata/Kaiko):

| Metric | Target (Majors) | Notes |
|---|---|---|
| **24h Spot Volume / Market Cap** (Liquidity Turnover Ratio) | >5–10% = healthy | Measures real trading activity |
| **±2% Order-Book Depth** (Binance, Bybit, OKX) | $100M+ for majors | Core structural depth metric |
| **Bid-Ask Spread** | <0.05–0.1% ideal | Tight = efficient market |
| **Slippage (realistic sizes)** | <0.5% for $1M–$10M orders | Excellent exit capability |
| **Derivatives Liquidity** | Perps vol vs. spot, OI sustainability | Cross-market depth |

**Stress Test**: Simulate a **$1M**, **$5M**, and **$10M** market sell. Does the price slip >1%? If yes, the asset is **structurally fragile**.

### 2.2 Why Liquidity Is Make-or-Break
- **High liquidity** = exit huge positions (100+ BTC, 10k+ ETH) with minimal slippage → lock in profits cleanly, compound small wins.
- **Low liquidity** = massive slippage eats gains, or you're trapped (price moves against you while selling).
- Liquidity dries up in bears → cascades worsen. Concentrate on bulls → easier big exits.
- Majors (BTC) have structural depth; alts can evaporate overnight.
- Institutions provide liquidity (market-making) but pull it in stress → watch depth contraction as early warning.
- On-chain/DEX liquidity matters for alts (Uniswap pools); CEX dominates spot for majors.
- **Timing**: Enter during rising volume/depth; exit in high-volume windows; avoid thin books (e.g., weekends, low-activity periods).

### 2.3 Cost Basis Analysis
- **Metric**: Identify the "Realised Price" (average on-chain acquisition price) for the entire network and specifically for Short-Term Holders.
- **Signal**: Price trading below the Short-Term Holder Realised Price typically indicates **"Extreme Fear"** and a potential capitulation bottom.

---

## Phase 3: Derivatives & Sentiment (The Volatility Layer)

**Goal**: Predict the next violent price move.

### 3.1 Institutional & Leverage Cycle Detection
- Collateral use: Borrow against holdings, basis trades, short setups on negative funding.
- **Cycle**: Accumulate → leverage amplify → sell into strength → re-accumulate lower.

### 3.2 Liquidation Heatmaps
**Action**: Map out leverage clusters (high-value liquidation levels).

- **Interpretation**: Price acts as a magnet to liquidity. If a massive cluster of Longs exists 5% below the current price, assume the market maker will push the price there to capture that liquidity.
- Cascade risk (downside liqs) vs. squeeze potential (upside).

### 3.3 Funding & Open Interest
- Open Interest (OI), funding rates, liquidation clusters (Coinglass, Hyblock Capital).
- **Check**: Is OI rising whilst price falls? → Aggressive shorting → **Squeeze potential**.
- **Check**: Is the Funding Rate negative? → Bearish sentiment, potentially overcrowded shorts.

---

## Phase 4: The Synthesis & Blueprint Score

**Goal**: Combine all distinct data points into a single actionable rating.

### 4.1 The Synthesis Equation
Construct a narrative sentence using this formula:

```
[Supply Constraint Status] + [Holder Behaviour] + [Market Structure Integrity] + [Derivatives Positioning] = [Conclusion]
```

**Example**: *"Fixed supply + 15% permanently illiquid + 45% of supply underwater + Rising Institutional inflows = Classic Discount Zone."*

### 4.2 The Blueprint Score (0–100)

| Component | Weight | High Score Means… |
|---|---|---|
| **Scarcity / Supply Integrity** | 30 pts | Deflationary, whales accumulating |
| **Liquidity / Depth** | 30 pts | Can exit a large position safely |
| **On-Chain Sentiment** | 20 pts | "Capitulation" = High Score; "Euphoria" = Low Score |
| **Derivative Structure** | 20 pts | Leverage flushed out (clean market) |

### 4.3 Final Verdict
- **Rating**: Strong Buy · Accumulate · Neutral · Distribute
- **Execution Strategy**:
  - **Entry Trigger**: e.g., *"Enter on positive funding flip"*
  - **Exit Trigger**: e.g., *"Trail stop on liquidity contraction"*
- **Enter**: Scarcity improving + institutional accumulation + balanced leverage + strong liquidity.
- **Exit/Trail**: Over-leverage extremes + liquidity thinning + institutional sell signals.
- **Goal**: Consistent small profits that compound safely (because liquidity lets you take them).

---

## Red Flag "Kill Switch" Checklist

> [!CAUTION]
> If **any** of the following are `True`, automatically set the Blueprint Score to **< 20**.

### Thin Order Books
**Trigger**: ±2% depth < $500k for a token with >$100M Market Cap.

**Why**: Indicates a **Liquidity Trap**. High market caps can be "zombie" valuations inflated by a few trades. A modest sell-off (e.g., £50k profit) could cause a 5–10% price crash (slippage).

**Kill Switch Logic**: If you cannot exit your position without destroying the price, your "gains" are purely theoretical. It's a sign the asset lacks "Institutional Grade" support.

### Supply Influx (Unlock Cliff)
**Trigger**: >15% of supply unlocking in the next 30 days.

**Why**: This is a **Dilution Event**. When a large "cliff" occurs, the market is hit with a massive increase in sellable supply. Historical data shows 90% of tokens experience negative price pressure 30 days before an unlock as traders "front-run" the dump.

**Kill Switch Logic**: Even with high demand, the sheer volume of new tokens often overwhelms buy orders. It is mathematically difficult for price to appreciate when 15% of the network is looking for the "Exit" door simultaneously.

### Concentration Risk (Whale Dominance)
**Trigger**: Top 10 wallets (excluding CEX/Contracts) hold >80% of supply.

**Why**: This is a **Centralisation Failure**. If a handful of individuals control the majority of the supply, the "market" isn't a market — it's a playground for those 10 people. They can coordinate a "Pump and Dump" or crash the price accidentally by moving funds.

**Kill Switch Logic**: You are essentially betting on the benevolence of 10 strangers. "Whale" movements trigger panic in retail, leading to cascading liquidations that you cannot predict with standard technical analysis.

### Artificial Volume (Wash Trading)
**Trigger**: Volume/Market Cap ratio > 1.0 (indicating fake volume).

**Why**: Indicates **Fake Demand**. In healthy markets, it is rare for the entire market cap to trade hands in a single 24-hour period. A ratio > 1.0 often means bots are trading the same tokens back and forth to climb exchange rankings and lure in unsuspecting buyers.

**Kill Switch Logic**: Wash trading masks the true liquidity. You might see "$500M Volume" and think it's safe to buy, only to find that when you try to sell, there are no real human buyers on the other side.

---

## Source Layer (Unique Alpha Only)
- **Core**: CoinGecko, Arkham, Glassnode
- **Unique**: [Ultrasound.money](https://ultrasound.money/) (burns), [Coinglass](https://www.coinglass.com/) (leverage/liquidity), Dune (custom), Hyblock (heatmaps), Amberdata/Kaiko (depth data), Nansen (on-chain labels)

---

**Version History**
- v1.0 (Feb 2026): Initial token analysis blueprint
- v1.1 (Feb 2026): Enhanced with 4-phase forensic framework, Blueprint Score (0–100), Kill Switch checklist, cost basis analysis, and synthesis equation
- Future: Add DeFi, NFT, fraud detection blueprints in this folder

**Maintained by**: Africa's Blockchain Club Research Team