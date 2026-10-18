# Education, Not Advice

This platform teaches people how to research a crypto token. It must never act as a financial adviser. This document sets out why, what the code does to enforce it, and the rules every contributor and every fork must keep.

> This document explains how the platform is designed. It is not legal advice. If you run a fork in public, especially one that charges real money, get advice from someone qualified in the law where you operate.

## Why the line matters

In South Africa, the Financial Sector Conduct Authority (FSCA) declared crypto assets a financial product under the Financial Advisory and Intermediary Services Act (FAIS) in 2022. Since then, giving advice about crypto assets, such as recommending that someone buy, sell or hold a token, has required authorisation as a financial services provider. Other countries have their own rules, and many treat recommendations in the same way.

Check the current position on the FSCA website before you rely on this summary. The rules change, and this file can fall behind them.

Explaining facts is different from recommending an action. This platform stays on the explaining side:

| Education (allowed) | Advice (never) |
|---|---|
| "Fully diluted value is 4 times market cap, so many tokens are still to be released." | "Avoid this token because of dilution." |
| "A $100,000 sale would move the main pool's price by about 2%." | "This token is too illiquid for large positions." |
| "Futures traders are paying to hold long positions." | "Bullish signal." |
| "Developments that would strengthen the project: ..." | "Bull case: 40% probability." |
| A list of risk checks, each Flagged, Clear or No data | A score out of 100, or Strong Buy to Strong Sell |

## What changed from v2.0

The v2.0 platform produced a Blueprint Score, a Buy/Sell verdict, entry and exit triggers, a Long-Term Conviction Score and an "AI Investment Brief" tailored to the reader. Each of those is a recommendation, and tailoring is what makes a recommendation personal. All of them are gone:

- The **score and verdict** are replaced by ten rule-based **risk checks** (`data_analytics/risk_profile.py`). They are never added together.
- The **phase signals** (bullish, bearish) are replaced by plain descriptions of what market participants are doing.
- The **forecast and scenario probabilities** are replaced by "developments that would strengthen or weaken the project".
- The **tailored brief** is removed. The platform does not ask who the reader is or what they want.
- The reports written under v2.0 are removed from the repository. They remain in the git history, which is why this file exists: read them as the "before" picture.

## How the code enforces it

A prompt is a request, not a control. The model is asked not to give advice, and then the code checks:

1. **The advice-language guard** (`data_science/compliance.py`). Every AI write-up is scanned for ratings, trading signals, entry and exit points, target prices, position sizing, valuation judgements and personal instructions. A write-up that fails is rejected with the phrases it used, and nothing is saved.
2. **The structure check** (`data_science/ai_generator.py`). A write-up with missing sections is rejected, so a cut-off answer is never published as a whole report.
3. **Code-owned sections** (`tools/report_store.py`). The disclaimer, the risk checks and the sources section are written by code, not by the model, so a model cannot drop or reword them.
4. **The data-only report** (`data_analytics/data_report.py`). It contains no model-written text and passes the same guard.
5. **Tests** (`tests/test_compliance.py`, `tests/test_report_generator.py`). The guard is tested against advice phrases and against teaching sentences that must still pass.

## The payment demo

The payment feature is switched off by default (`PAYMENTS_ENABLED=false`). When it is on, it takes test USDC on the Base Sepolia test network, which has no real-world value. It exists to teach how on-chain payments work. The screen and the receipt say that the payment covers the computing cost of the write-up, not advice.

A fork that charges real money for reports moves closer to running a paid research service. Do not do that without qualified advice.

## Rules for contributors

1. Never add a score, rating, verdict, grade, ranking or target price for a token, in code, prompts, the interface or documentation.
2. Never add a feature that asks about the reader's money, goals or circumstances, or tailors output to them.
3. Every new risk check must have three states (flagged, clear, no data), a stated teaching threshold, a source, and an explanation of what it means, not what to do.
4. If you change the AI prompt, run `pytest` and read a real write-up before you merge.
5. If the guard rejects a sentence that is genuinely educational, narrow the pattern and add the sentence to the `TEACHING` list in `tests/test_compliance.py`. Never delete a pattern to make a write-up pass.
6. Keep the disclaimer on every page and in every report.
