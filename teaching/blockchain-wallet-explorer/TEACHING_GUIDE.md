# Teaching Session Guide — Blockchain Data Science Walkthrough

A step-by-step script for running this project as a live demo for students new to blockchain.

---

## Who it's for

Students who are blockchain beginners but already comfortable reading and running basic JavaScript/Node. No crypto trading experience or capital required — it's read-only, runs on a free testnet (Scroll Sepolia), and needs no real ETH. Good fit for a "first contact with blockchain data" session, e.g. CS/data-science students, junior devs moving into Web3, or analysts learning the fundamentals behind tools like Chainalysis/Elliptic/Nansen.

## Why it's important

Most blockchain intros are either pure theory (whitepapers, diagrams) or a wallet-and-token tutorial that stops at "send a transaction." This project skips both and goes straight to the *analyst's* perspective: instead of just using a wallet, students learn to **read** the chain — balances, transaction history, and multi-hop fund flows — which is the actual skill blockchain forensics and compliance teams use.

**Opening line for students:**
> "Today you're not a crypto user, you're a chain analyst. By the end, you'll be able to look at any wallet address and answer: what does it hold, who has it talked to, and where did its money come from."

## When to use it

- As a 45–60 minute hands-on lab right after a conceptual intro to blockchain (don't lead with this — lead with 10 minutes of "what is a blockchain/wallet/token," then hands-on).
- As the on-ramp before introducing real analytics platforms, so students have built the primitives themselves first.
- **Not** a fit for teaching smart contract development, DeFi mechanics, or consensus — it's strictly about reading chain data, not writing to it.

---

## Setup (before the session, or live as a 5-minute "this is how every blockchain project starts")

```bash
npm install
cp .env.example .env
```

Then fill in `.env`:
- `RPC_URL` — Scroll Sepolia RPC: `https://sepolia-rpc.scroll.io`
- `TOKEN` — the ERC20 token address to track
- `CONTRACT` — a contract/wallet address whose balance to check
- `ETHERSCAN_API_KEY` / `BLOCKSCOUT_API_KEY` — free testnet keys (links in README)

**Say:** "Every blockchain project starts the same way — an RPC endpoint to talk to the chain, and API keys for the indexing services that make history queries fast."

---

## Step 1 — Keys & Addresses

```bash
node createWallets.js
```

**Say while output scrolls:** "Each wallet you see has three things: an address (public, like a bank account number), a private key (secret, proves ownership), and a mnemonic (a human-readable backup of the private key). This is exactly what MetaMask generates when you click 'create wallet' — we're just doing it in code so you see what's normally hidden."

**Optional live variant — HD wallets:**
Open `createWallets.js`, comment out `createWallets();` and uncomment `createDeterministicWallets();` at the bottom, then rerun:

```bash
node createWallets.js
```

**Say:** "Notice the derivation path `m/44'/60'/0'/0/i`. All five wallets came from *one* seed phrase. This is why a single 12-word backup phrase can restore unlimited wallets — hardware wallets and MetaMask use this same standard (BIP-44)."

**Ask the room:** "Why might it be useful to track a wallet you don't own?" → bridges into Step 2's watch-only trick later.

---

## Step 2 — ERC20 Tokens & ABIs

```bash
node checkBalances.js
```

**Say:** "Open `checkBalances.js` and look at the ABI array — just three function signatures: `balanceOf`, `symbol`, `decimals`. That's the entire contract interface ethers.js needs. You don't need the contract's source code, just the shape of the functions you intend to call."

**Point out:** the `0n` BigInt literal. **Say:** "Token balances are stored on-chain as raw integers that can exceed JavaScript's safe number range, so we use BigInt instead of regular numbers — this is a common gotcha for blockchain beginners."

---

## Step 3 — Transaction History & Indexers

```bash
node checkInteractions.js
```

**Say:** "Look at Method 1 in this file — it's deliberately left as a stub. Ethers v6 removed `provider.getHistory()`, meaning a raw blockchain node *cannot* cheaply answer 'show me this wallet's history.' That's exactly why indexing services like Blockscout and Etherscan/Scrollscan exist — Method 2 uses their API instead."

**Concept to land:** the layered architecture of blockchain infrastructure — raw node → indexer → analytics tool. This is the same stack real analytics firms build on.

---

## Step 4 — Multi-Hop Transaction Graphs

First, run it with no API key set (or temporarily comment out the key in `.env`) to get the clean simulated graph:

```bash
node simulateInteractions.js
```

**Say:** "With no real data, the script falls back to a simulation so you can see a clean example of a transaction graph before we look at messy real data."

Then add the key back to `.env` and rerun the *same* command:

```bash
node simulateInteractions.js
```

**Say:** "Now look at `findAllPaths` in the code — it's a depth-first search over a directed graph of wallet-to-wallet transfers. This is, structurally, the same technique used to trace funds through mixers and multi-hop laundering schemes in real forensic investigations."

---

## Optional Closer — Watch a Real Wallet

No script to run yet — manually edit `wallets.json` and add an entry for any real address you don't own (an exchange wallet, a known contract, etc.):

```json
{
  "id": 6,
  "address": "0xYourInteractedWalletAddress",
  "privateKey": "WATCH_ONLY",
  "mnemonic": "WATCH_ONLY"
}
```

Then rerun:

```bash
node checkBalances.js
node checkInteractions.js
```

Open the same address in a browser side-by-side:

```
https://sepolia.scrollscan.com/address/0xYourAddressHere
```

**Say:** "Compare what our script printed to what the official explorer shows. They should agree — that's how you know the script is reading real chain data, not just simulating."

---

## Quick Reference — Full Command Sequence

```bash
npm install
node createWallets.js
node checkBalances.js
node checkInteractions.js
node simulateInteractions.js
```

Equivalent via `npm` scripts:

```bash
npm run create-wallets
npm run check-balances
npm run check-interactions
npm run simulate
```
