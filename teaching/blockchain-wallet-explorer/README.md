# Blockchain Data Science - Hands-On Walkthrough

This project is a practical introduction to on-chain data analysis using Ethereum and ethers.js.  
You will learn how wallets work, how to read token data from the blockchain, and how to trace money moving between addresses - the same techniques used by blockchain analytics firms like Chainalysis, Elliptic, and Nansen.

---

## What You Will Build Intuition For

| Concept | Covered In |
|---|---|
| How private keys, public keys, and addresses relate | `createWallets.js` |
| What an HD (hierarchical deterministic) wallet is | `createWallets.js` |
| What an ERC20 token is and how to read it | `checkBalances.js` |
| What an ABI is and why you need it | `checkBalances.js` |
| What an RPC node is and why it matters | all scripts |
| How to query transaction history | `checkInteractions.js` |
| How to trace multi-hop fund flows | `simulateInteractions.js` |
| What a transaction graph is | `simulateInteractions.js` |

---

## Prerequisites

- [Node.js](https://nodejs.org/) v18 or higher (`node -v` to check)
- Basic JavaScript comfort (you don't need to be an expert)
- A free Scrollscan API key at https://scrollscan.com/myapikey
- A free Blockscout API key at https://blockscout.com (used as primary by the scripts)
- No ETH needed - Scroll Sepolia is a testnet and the scripts are read-only by default

---

## Setup (do this once)

**1. Install dependencies**
```bash
npm install
```

**2. Create your environment file**
```bash
cp .env.example .env
```

**3. Fill in `.env`**

Open `.env` and add:
- `RPC_URL` - Scroll Sepolia RPC: `https://sepolia-rpc.scroll.io`
- `TOKEN` - the ERC20 token address you want to track
- `CONTRACT` - a contract or wallet address whose token balance you want to check
- `ETHERSCAN_API_KEY` - your Scrollscan API key (get one free at https://scrollscan.com/myapikey)
- `BLOCKSCOUT_API_KEY` - your Blockscout API key (get one free at https://blockscout.com) - used as primary when present

> **This project runs on Scroll Sepolia testnet.** You do not need real ETH. The scripts are read-only by default - they only send transactions if you explicitly uncomment that section in `simulateInteractions.js`.

---

## Running the Scripts

Run these in order the first time:

```bash
npm install
node createWallets.js        # generate your 5 wallets
node checkBalances.js        # see token balances on Scroll Sepolia
node checkInteractions.js    # pull real tx history via Blockscout
node simulateInteractions.js # trace interaction paths
```

---

## Tracking a Wallet You Interacted With

If you want the scripts to include an external wallet you interacted with (one you don't own), add it to `wallets.json` as a watch-only entry after running `createWallets.js`:

```json
{
  "id": 6,
  "address": "0xYourInteractedWalletAddress",
  "privateKey": "WATCH_ONLY",
  "mnemonic": "WATCH_ONLY"
}
```

The scripts will track its balances and interactions alongside your own wallets without needing its private key.

---

## Viewing Any Address on Scrollscan

To inspect any address visually in your browser:

```
https://sepolia.scrollscan.com/address/0xYourAddressHere
```

On that page:
- **Transactions tab** - every ETH transaction sent or received
- **Token Transfers tab** - ERC20 movements (filter by your token contract to find specific interactions)
- **Internal Txns** - transfers triggered by smart contracts

To find interactions with a specific token, click **Token Transfers** and look for your token's contract address in the contract column.

---

## Module 1 - Wallets: Keys, Addresses, and Identity

**File:** `createWallets.js`  
**Run:** `node createWallets.js`

### What happens
The script generates 5 Ethereum wallets and saves them to `wallets.json`.

### What to study after running it

Open `wallets.json`. For each wallet you'll see three things:

```
privateKey  →  the secret. Whoever has this controls the wallet.
address     →  the public identifier. Safe to share.
mnemonic    →  a human-readable backup of the private key (12-24 words).
```

**The relationship:** `private key → (elliptic curve math) → public key → (hashing) → address`  
The address is derived from the private key, but you cannot reverse the process. This is why addresses are safe to share.

### Exercise A - Random vs Deterministic wallets
Edit `createWallets.js`, comment out `createWallets()` and uncomment `createDeterministicWallets()`. Run it again.

Now look at the new `wallets.json`. All 5 wallets came from **one master mnemonic** using different derivation paths (`m/44'/60'/0'/0/0`, `m/44'/60'/0'/0/1`, etc.).

This is how every Ethereum wallet app (Metamask, Ledger, Trust Wallet) works internally. The 12-word seed phrase you back up IS the master mnemonic. From it, the app derives as many addresses as you need.

**Key insight:** With random wallets, losing the file means losing the wallet forever. With deterministic wallets, one mnemonic recovers everything.

### What to research further
- BIP-39 (mnemonic standard)
- BIP-44 (derivation path standard)
- Elliptic Curve Digital Signature Algorithm (ECDSA) - the math behind Ethereum addresses

---

## Module 2 - Token Balances: Reading Smart Contract State

**File:** `checkBalances.js`  
**Run:** `node checkBalances.js`

### What happens
The script connects to Ethereum, reads the token balance of each of your 5 wallets plus one contract address, then prints a total.

### Concepts to understand

**RPC Node (your `RPC_URL`)**  
You don't store the blockchain yourself. Instead you connect to a node that does, and send it JSON-RPC requests. Alchemy and Infura run these nodes as a service. Free tiers are sufficient for this project.

**ABI (Application Binary Interface)**  
A smart contract is compiled code sitting on the blockchain. The ABI is the translation layer - it tells ethers.js which functions exist and what types they accept and return. You only need to include the functions you actually call:
```js
"function balanceOf(address) view returns (uint256)"
"function symbol() view returns (string)"
"function decimals() view returns (uint8)"
```

**Why `decimals` matters**  
Token amounts on-chain are always integers. A token with 6 decimals stores `1,000,000` to represent `1.0`. USDC uses 6 decimals; most tokens use 18. `ethers.formatUnits(rawAmount, decimals)` converts the raw integer to a human-readable number.

**BigInt (`0n`)**  
JavaScript's regular `number` type cannot safely handle 18-decimal Ethereum amounts - they overflow. ethers.js uses `BigInt` (the `n` suffix). This is why the balance accumulator is `let total = 0n`.

### Exercise B - Point it at a real token
Set `TOKEN` in `.env` to any ERC20 token address from [Etherscan's token tracker](https://etherscan.io/tokens). Set `CONTRACT` to the token's own address or a known protocol address (e.g. Uniswap's router). Run the script and observe the balance.

Your 5 wallets will show 0 - they are fresh and hold nothing. That is correct.

### What to research further
- ERC20 standard (EIP-20) - the 6 functions every token must implement
- How `eth_call` works vs `eth_sendTransaction`
- Gas and why read calls (`view` functions) are free

---

## Module 3 - Transaction History: Who Sent What to Whom

**File:** `checkInteractions.js`  
**Run:** `node checkInteractions.js`

### What happens
The script checks whether any of your 5 wallets have sent ETH or tokens to each other. It offers three methods and explains when each applies.

### The three data methods

**Method 1 - Block scanning**  
In theory you could scan every block looking for transactions involving your addresses. In practice this is slow and ethers v6 removed the convenience helper for it. You'd need an archive node (expensive) or a service like Alchemy's `alchemy_getAssetTransfers` API endpoint. This method is included for educational completeness.

**Method 2 - Etherscan API**  
Etherscan has already indexed all transactions. You send an address, they return its full transaction history instantly. This is what most tools use. Free API key gives you 5 requests/second.

**Method 3 - ERC20 Transfer events**  
Every ERC20 transfer emits a `Transfer(from, to, value)` log event. You can query these events directly from the node using `queryFilter`. This is more targeted than scanning all transactions and is ideal when you care about a specific token.

### Why your wallets show no interactions
Your wallets are freshly generated - they have no history. This is the expected result. The script is designed to work with real wallets that have actual on-chain history.

### Exercise C - Analyse a real address
Replace one entry in `wallets.json` with a real address you know has activity (e.g. a public wallet from etherscan.io). Run the script and observe the output.

### What to research further
- How Ethereum event logs work (topics, indexed parameters)
- Archive nodes vs full nodes vs light nodes
- The Graph Protocol - a decentralised indexer used as an alternative to Etherscan

---

## Module 4 - Interaction Chains: Tracing Money Through Multiple Hops

**File:** `simulateInteractions.js`  
**Run:** `node simulateInteractions.js`

### What happens
If you have Etherscan data, it analyses real paths. If not (expected with fresh wallets), it runs a simulation so you can see the output immediately.

This script answers the question: *"Starting from Wallet 1, through how many intermediaries can it reach Wallet 4?"*

### Why this matters - blockchain forensics
Money laundering on-chain typically involves **layering**: funds move through multiple wallets to obscure their origin. A direct transfer from a flagged wallet to an exchange is easy to detect. A 5-hop chain is harder - but the blockchain records every step permanently.

Blockchain analytics firms build exactly this kind of graph analysis at scale. This script is a minimal version of that.

### How the algorithm works
The script builds a **directed graph** where:
- Each node is a wallet address
- Each directed edge is a transaction from one wallet to another

Then it runs **depth-first search (DFS)** to find all paths between any two nodes, up to 5 hops deep. The output tells you: *"There are 3 paths from Wallet 1 to Wallet 4, the shortest being 2 hops."*

### Exercise D - Simulate and extend
Run the script and read through the simulated output. Then:

1. Open `simulateInteractions.js` and find the `simulatedInteractions` array.
2. Add a new edge - for example a transaction from `w5` to `w1`.
3. Run it again. Notice how the path options change.
4. Increase `maxDepth` from 5 to 7. What changes?

### Exercise E - Send real transactions (optional, requires testnet ETH)
1. Switch your `RPC_URL` to Sepolia testnet in `.env`
2. Get free Sepolia ETH from a faucet (search "Sepolia faucet")
3. Fund Wallet 1's address with the testnet ETH
4. In `simulateInteractions.js`, uncomment `createRealInteractions()` inside `main()`
5. Run the script - it will send 3 real testnet transactions: Wallet 1→2→4→3
6. Re-run the script - this time it will find and display real on-chain paths

### What to research further
- Graph theory fundamentals (nodes, edges, DFS, BFS)
- Chainalysis and Elliptic - read their public research reports
- UTXO vs Account model (Bitcoin vs Ethereum transaction tracing differences)

---

## File Reference

| File | Purpose |
|---|---|
| `createWallets.js` | Generate wallets, save to `wallets.json` |
| `checkBalances.js` | Read ERC20 token balances from the blockchain |
| `checkInteractions.js` | Find transactions between your wallets |
| `simulateInteractions.js` | Build interaction graph and trace multi-hop paths |
| `.env.example` | Template - copy to `.env` and fill in your keys |
| `wallets.json` | Generated file - your wallet data (gitignored) |
| `interactions.json` | Generated file - saved interaction data (gitignored) |

---

## Learning Path Beyond This Project

Once comfortable here, explore these in order:

1. **Alchemy SDK** - higher-level APIs for transaction history, NFT data, token balances across all wallets
2. **The Graph** - query indexed blockchain data with GraphQL instead of raw RPC calls
3. **Dune Analytics** - write SQL against indexed Ethereum data; used by researchers and analysts professionally
4. **Foundry or Hardhat** - deploy your own test contracts and interact with them using these same tools
5. **MEV (Maximal Extractable Value)** - a data-rich research area; start with Flashbots' public documentation
