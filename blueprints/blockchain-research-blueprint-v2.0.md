# The Blockchain Research & Blueprint Protocol
**Liquidity-First Forensic Research on a Token and the Blockchain It Lives On**

**Objective**: Produce a forensic research report on **[TOKEN NAME]** that covers the full stack: the macro environment the blockchain trades in, the chain's own health and trajectory, the protocol's fundamentals, on-chain supply dynamics, market structure liquidity, derivative positioning, and a one-to-five year outlook.

**Scope**: This is not token analysis alone. A token is only as strong as the blockchain it runs on, and a blockchain is only as strong as the macro environment and the developers building on it. The report therefore researches three layers - the chain, the protocol, and the token - and scores them separately.

**Output Standard**: Two scores, both 0-100:
- The **Blueprint Score** answers "is now a good time to enter?"
- The **Long-Term Conviction Score** answers "is this worth holding for years?"

All maths and formulas MUST be plain text markdown (e.g. `100 / 50 = 2`). LaTeX syntax is strictly forbidden - it breaks PDF rendering.

**Audience**: Written for two readers at once. Experienced investors get the numbers first (every phase leads with a data table). Blockchain developer prospects and community members learning to read research get an educational callout after every table (`> **Reading this table:** ...`) and inline definitions of every technical term on first use.

---

## The ABC Research Methodology

This blueprint applies the Research section of the Africa's Blockchain Club curriculum. Every report walks the same eight steps:

1. **Define the objective** - what decision is this research meant to support?
2. **Identify sources** - where does trustworthy data live, and what does each source actually measure?
3. **Analyse the technology** - the chain, the protocol, and how the token's trading mechanics work.
4. **Study market data** - supply, liquidity, derivatives, price structure.
5. **Evaluate team and community** - developer activity, holder behaviour, social narrative.
6. **Assess regulatory risk** - classification, compliance, delisting exposure.
7. **Perform SWOT analysis** - strengths, weaknesses, opportunities, threats.
8. **Document findings** - with a Blueprint Score, a Conviction Score, and specific entry and exit triggers.

**Phase Signal Rule**: every phase ends with a one-line verdict callout - `> **Phase [X] Signal: [BULLISH / BEARISH / NEUTRAL]**` - naming the single most important number found in that phase and the action it implies. A reader skimming only the signals gets the whole argument.

---

## Report Structure

The report opens with a **How to Read This Report** panel: Phase 0 tells you the story and the context. Phase 1 tells you what actually exists on-chain. Phase 2 tells you whether you can buy or sell at scale without moving the price. Phase 3 tells you what leveraged traders are doing. Phase 4 synthesises everything into a score and a verdict. Phase 5 steps back from the 24-hour data and forecasts the chain, the protocol, and the token over one to five years.

---

## Phase 0: Overview & Narrative (The Social Layer)

**Goal**: before any numbers, capture what the market believes about this token right now, and what the macro environment is doing to that belief. Price follows story.

### 0.1 Token Snapshot
Four grouped landscape tables, full width: **Identity** (name, symbol, chain, category, DEX), **Price & Performance** (USD, ZAR, 24h/7d/30d change), **Market Size & Value** (market cap, ATH, % below ATH, FDV), **Supply**.

### 0.2 Recent News & Social Sentiment
A table of real, current headlines (source, date), then commentary naming the dominant narrative. The key distinction: a **structural catalyst** (exchange listing, protocol upgrade, institutional backing) has lasting price impact; **short-term noise** (speculation, rumours) does not. The report must say which one it is and why that matters for the holding period.

### 0.3 Macro Environment Context
This is where the research widens beyond the token to the world its blockchain trades in. A table covering: Fed policy stance, the QE/QT cycle, M2 money supply trend, the yield curve, USD strength (DXY), global risk appetite, and the crypto regulatory climate - each with its direct impact on this token. Commentary names the single biggest macro risk and the single biggest macro tailwind.

---

## Phase 1: The Hard Data (Supply Forensics)

**Goal**: determine the true circulating supply versus the theoretical supply.

- **1.1 Supply Overview** - circulating, total, and max supply; FDV versus market cap (FDV far above market cap signals future dilution).
- **1.2 Tokenomics & Distribution** - fixed versus dynamic supply, burn versus issuance, unlock schedule.
- **1.3 Sovereign & Institutional Inventory** - labelled entity holdings, distinguishing **forced sellers** (governments, trustees) from **strategic holders** (treasuries, ETFs). One is supply overhang, the other is a supply sink.
- **1.4 Permanent Scarcity Layer** - effective supply after removing dormant coins and burn addresses:
  ```
  Effective Supply = Total Supply - (Coins unmoved > 5 years) - (Burn addresses)
  ```

## Phase 1.5: Tokenomics & AMM Math

**Goal**: show, with this token's real pool numbers, how an AMM (Automated Market Maker - a DEX that prices assets with a formula instead of an order book) actually sets the price.

- **1.5.1 Liquidity Pool Equation** - the constant product formula `x * y = k`, explained in plain English before the calculation, then computed from the live pool's base and quote token balances.
- **1.5.2 Pool Split** - what sits on each side of the pool and what that implies for exit capacity.

---

## Phase 2: Market Structure (The Liquidity Layer)

**Goal**: assess whether the market can support an exit without slippage.

> **Principle**: profit is theoretical; liquidity is realised.

- **2.1 Liquidity Metrics** - pool liquidity (USD and ZAR), 24h volume, **Turnover Ratio** (volume / market cap - above 100% is a wash-trading red flag), and **Depth-to-MCap Ratio** (liquidity / market cap - below 1% means the market is fragile). Depth-to-MCap is the single most important number in this section.
- **2.2 Stress Test** - simulated market sells at $50K, $100K, $500K, $1M, and $5M, with estimated slippage calculated from the actual pool depth using the constant product formula. Slippage above 5% on $100K means the token cannot support institutional-size positions.
- **2.3 Cost Basis Analysis** - the Short-Term Holder (wallets that acquired within the last 155 days) cost basis. Price below the STH cost basis means recent buyers are underwater and will sell into any recovery, creating resistance.

## Phase 2.5: DeFi Mechanics

**Goal**: establish whether the protocol behind the token has genuine usage or is purely speculative.

- **2.5.1 Protocol Infrastructure** - TVL (Total Value Locked, the best available proxy for protocol trust), category, chains, primary DEX, and AMM type. TVL falling while price rises is a red flag: price disconnected from real usage.

---

## Phase 3: Derivatives & Sentiment (The Volatility Layer)

**Goal**: predict the next violent price move by reading what leveraged traders believe.

- **3.1 Derivatives Overview** - Open Interest (OI), 24h derivatives volume, funding rate, and OI-versus-price divergence. Rising OI with rising price is bullish (new longs); rising OI with falling price is bearish (shorts piling in); extreme funding on high OI is the setup for a liquidation cascade.
- **3.2 Liquidation Heatmap Summary** - price levels with clustered liquidations act as magnets; price often moves toward them because large traders know where the stops are.

---

## Phase 4: The Synthesis & Blueprint Score

**Goal**: combine every layer into one actionable rating.

### 4.1 Synthesis Equation
```
[Supply Constraint Status] + [Holder Behaviour] + [Market Structure Integrity] + [Derivatives Positioning] = [Conclusion]
```

### 4.2 Blueprint Score (0-100)
Four components, each scored against explicit criteria bands so two analysts reach the same number:

| Component | Weight | Top band requires | Bottom band means |
|---|---|---|---|
| Scarcity / Supply Integrity | 30 | FDV < 2x MCap, circulating > 70%, no unlock cliff | FDV > 10x MCap, unlock cliff > 15%, or top 10 wallets > 80% |
| Liquidity / Depth | 30 | Depth-to-MCap > 5%, $1M trade < 1% slippage | Thin-book Kill Switch, or $100K trade > 5% slippage |
| On-Chain Sentiment | 20 | Price in accumulation zone, structural catalyst present | Artificial-volume Kill Switch, or negative narrative with no catalyst |
| Derivative Structure | 20 | OI aligned with price, funding near neutral | Cascade imminent, or derivatives data completely unavailable |

Score interpretation: 80-100 Strong Buy conditions; 60-79 Accumulate; 40-59 Neutral; 20-39 Distribute; below 20 Kill Switch triggered - do not hold.

### 4.3 SWOT Analysis
Internal factors from the token data; external factors from the macro environment, regulatory landscape, and competitive market structure.

### 4.3.5 Investment Decision Checklist
Five questions answered with actual values from the report: score above 60? Any Kill Switch? Macro supportive? Can $100K exit under 3% slippage? Is the narrative structural or noise?

### 4.4 Final Verdict
Rating (Strong Buy / Accumulate / Neutral / Distribute / Strong Sell), plus **Entry Trigger** and **Exit Trigger** that MUST reference a specific price level, ratio, or threshold from this report - never a generic condition. Primary risk, secondary risk, time horizon.

---

## Red Flag Kill Switch Assessment

> [!CAUTION]
> If any of the first four are triggered, the Blueprint Score is overridden to below 20 regardless of other findings.

| Kill Switch | Trigger | Why it is dangerous |
|---|---|---|
| Thin Order Books | +-2% depth < $500k on a >$100M market cap | A modest sell order craters the price; gains are theoretical |
| Supply Influx | >15% of supply unlocking within 30 days | A predictable dilution cliff the market front-runs |
| Concentration Risk | Top 10 wallets hold > 80% | The market is a playground for ten strangers |
| Artificial Volume | Volume / Market Cap > 1.0 | Wash trading masks the absence of real buyers |
| SEC Security Classification Risk | Yes / No / Unclear | Regulatory action forces exchange delistings |
| FATF Non-Compliance Risk | Yes / No / Unclear | AML non-compliance triggers coordinated delistings |
| Exchange Delisting Risk | Yes / No / Unclear | Loss of major exchange access destroys liquidity |

Each triggered flag must be explained in plain English in the commentary - why it is dangerous in practice, not just Yes/No.

---

## Phase 5: Long-Term Outlook (1-5 Year Forecast)

**Goal**: this is where the research becomes about the blockchain itself. Short-term trades are won by liquidity and momentum; long-term wealth is built by being early to chains, protocols, and sectors with structural growth ahead of them. Honesty here is worth more than optimism, and the data caveat is stated up front: most tokens have under five years of live market data, so the Conviction Score reflects data availability as much as direction.

### 5.1 Underlying Chain Forecast
The foundation layer. A 1, 3, and 5 year outlook for the chain the token lives on: monthly active addresses, daily transaction volume, **developer activity** (the most reliable leading indicator of a chain's health - a chain losing developers is losing its future), chain TVL, network revenue, and competitor chains. If the token IS the chain's native asset (ETH, SOL), this section merges with 5.3.

### 5.2 Protocol Forecast
The business layer. TVL trajectory (crypto's closest equivalent to earnings growth), protocol revenue, user growth, FDV/TVL trajectory, competitive position, and - critically - **whether revenue accrues to token holders**. Fees that never reach holders make the token a bet on future governance, not current cashflow. Memecoins and pure governance tokens state N/A and skip to 5.3.

### 5.3 Token Forecast
The asset layer. Supply pressure trajectory, remaining unlock schedule, burn mechanisms, adoption-driven demand, regulatory trajectory, and sector alignment. The overlooked variable: a token whose supply keeps expanding with no demand offset dilutes holders no matter how well the protocol performs.

### 5.4 Scenario Analysis
Bull, Base, and Bear cases with **specific, observable trigger conditions** - not "if the market goes up" but "if monthly active addresses exceed X and FDV/TVL drops below Y". The Bear Case triggers are the exit signal: if they appear in a future report, the thesis is broken. Closes with a plain-English Long-Term Thesis paragraph that answers "is this worth holding for years?" with a yes or a no, defended.

### 5.5 Long-Term Conviction Score (0-100)
Separate from the Blueprint Score, with its own criteria bands:

| Component | Weight | What it measures |
|---|---|---|
| Adoption Trajectory | 25 | Active address and developer growth on the chain |
| Tokenomics Trajectory | 20 | Supply pressure direction and value capture |
| Regulatory Direction | 20 | Classification clarity and delisting exposure |
| Sector and Protocol Thesis | 20 | Structural sector growth and competitive moat |
| Cycle Positioning | 15 | Where entry sits in the market cycle |

Interpretation: 80-100 High Conviction (rare; 3-5 year hold); 60-79 Medium Conviction (1-3 years, quarterly monitoring); 40-59 Speculative; below 40 Low Conviction - structural headwinds outweigh growth.

**The two scores together**: high Blueprint + low Conviction means trade it, do not hold it. Low Blueprint + high Conviction means wait for a better entry, but this is worth owning.

---

## Source Layer

Every report ends with a table of the sources used, what each provides, and its reliability:

- **Primary**: DexScreener (pairs, pools, live pricing)
- **Core**: CoinGecko, DeFiLlama (TVL), CryptoPanic (news)
- **Derivatives**: CoinGlass (OI, funding, liquidations)
- **Chain-specific**: Ultrasound.money (ETH burn), block explorers
- Where a field is unavailable, the report writes N/A and states which data source would complete it - uncertainty is disclosed, never hidden.

---

## How the Pipeline Enforces This Blueprint

The system prompt in `data_science/ai_generator.py` enforces this structure exactly - the `## Phase` headings must not be renamed or the dashboard's phase navigation breaks. Reports are generated by a single Anthropic Claude model selected per request (Haiku to Fable tier), saved to `reports/{TOKEN}_audit_report.md` with a metadata header (Token, Score, Verdict, Model, Screenshot), and unlocked through on-chain payment verification before the paid AI stage runs.

**Adding a new research task**: create `blueprints/new-task-blueprint-v1.0.md` following this structure. The dashboard auto-detects blueprint files; no code changes needed.

---

**Version History**
- v1.0 (Feb 2026): Initial token analysis blueprint
- v1.1 (Feb 2026): 4-phase forensic framework, Blueprint Score, Kill Switch checklist, cost basis analysis, synthesis equation
- v2.0 (Jul 2026): Renamed from token-analysis to blockchain-research. Scope widened from the token to the blockchain itself: macro environment context (0.3), AMM math (1.5), DeFi mechanics (2.5), per-phase signal verdicts, explicit scoring criteria bands, regulatory kill switches, the investment decision checklist, and Phase 5 - the 1-5 year chain, protocol, and token forecast with a separate Long-Term Conviction Score. Aligned to the ABC curriculum Research methodology. Single-model Anthropic pipeline replaced the earlier multi-model race.

**Maintained by**: Africa's Blockchain Club Research Team
