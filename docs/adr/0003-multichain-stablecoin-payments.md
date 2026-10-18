# 0003: Stablecoin payments on six chains, verified on-chain

**Status:** Accepted, 18 October 2026

## Context
Payments started as test USDC on one testnet. Payers hold USDC or USDT on many networks and should not have to swap or bridge to pay 2 US Dollars.

## Decision
Accept USDC or USDT on Base, Arbitrum, Optimism, Polygon, BNB Chain and Ethereum, to one business wallet. The browser component reads the payer's balances, preselects one they can afford, switches the network and sends the transfer. The server trusts nothing from the browser: it verifies the transaction on-chain (recent, right contract, right recipient, full amount, enough confirmations) before any write-up runs.

## Options considered
- **Card payments through a South African gateway.** Wider reach, but a merchant account and more personal data; possible later as a second adapter.
- **One chain only.** Simpler, but forces many payers to bridge first.

## Consequences
Every token contract is checked on-chain before it is added. USDC and USDT are both counted as one US Dollar. A paid write-up that fails can be retried with the same transaction within the hour.
