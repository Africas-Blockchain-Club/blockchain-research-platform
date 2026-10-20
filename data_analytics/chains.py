"""
Blockchain profiles for the featured chains.

These are the stable facts a learner needs before any number makes sense:
what the chain is for, how it reaches agreement, how its native asset is
used, where to check, and its main client repository (for developer activity). Anything that changes week to week (fees, block
times, validator counts) is not written here; it comes live from
data_engineering/networks.py.

Every profile lists official sources and the date it was last checked. When
a fact changes (an upgrade, a new consensus rule), update the profile, the
CHECKED date, and the test in tests/test_chains.py.

The order of FEATURED is the order the site shows them in.
"""

CHECKED = "18 October 2026"

PROFILES = {
    "BTC": {
        "coingecko_id": "bitcoin",
        "repo": "bitcoin/bitcoin",
        "chain": "Bitcoin",
        "slug": "bitcoin",
        "asset": "BTC",
        "launched": "January 2009",
        "purpose": "The first blockchain: a peer-to-peer system for sending value without a bank, now used mainly as a store of value and for settling large transfers.",
        "consensus": "Proof of work. Miners compete to add each block by spending computing power (a hash function called SHA-256, one of the Secure Hash Algorithms); the chain with the most accumulated work is the valid one.",
        "programmability": "Deliberately limited scripting (Bitcoin Script). Faster, cheaper payments run on layers built above it, such as the Lightning Network.",
        "asset_role": "BTC pays transaction fees and the block reward that pays miners. Supply is capped at 21 million; the new issuance per block halves roughly every four years.",
        "uses": ["Store of value", "Settlement of large transfers", "Payments over the Lightning Network", "Collateral in other systems"],
        "learn_more": ["https://bitcoin.org/bitcoin.pdf", "https://developer.bitcoin.org/devguide/"],
    },
    "ETH": {
        "coingecko_id": "ethereum",
        "repo": "ethereum/go-ethereum",
        "chain": "Ethereum",
        "slug": "ethereum",
        "asset": "ETH",
        "launched": "July 2015",
        "purpose": "A general-purpose blockchain for programs (smart contracts), and the settlement layer that many layer 2 networks post their transactions to.",
        "consensus": "Proof of stake since September 2022 (the Merge). Validators lock 32 ETH each, propose and attest to blocks in 12-second slots, and lose stake if they cheat.",
        "programmability": "Full smart contracts on the Ethereum Virtual Machine (EVM, the software every Ethereum node runs to execute smart contracts), usually written in Solidity. Many other chains copy the EVM so the same code runs there.",
        "asset_role": "ETH pays for computation (gas) and is the stake that secures the network. There is no fixed supply cap; since August 2021 part of every fee is burned (a change made by EIP-1559, an Ethereum Improvement Proposal), which offsets new issuance.",
        "uses": ["Decentralised finance (DeFi)", "Stablecoins", "Tokens and NFTs", "Settlement for layer 2 rollups"],
        "learn_more": ["https://ethereum.org/en/developers/docs/", "https://ethereum.org/en/roadmap/merge/"],
    },
    "SOL": {
        "coingecko_id": "solana",
        "repo": "anza-xyz/agave",
        "chain": "Solana",
        "slug": "solana",
        "asset": "SOL",
        "launched": "March 2020 (mainnet beta)",
        "purpose": "A single fast chain designed for high throughput and low fees, so that payments, trading and consumer apps can run without a separate scaling layer.",
        "consensus": "Proof of stake, with Proof of History: a running cryptographic clock that orders transactions before validators vote on them.",
        "programmability": "Smart contracts are called programs, usually written in Rust. Transactions that touch different accounts run in parallel.",
        "asset_role": "SOL pays fees and is staked to validators. New SOL is issued to stakers at a rate that falls over time, and part of each fee is burned.",
        "uses": ["Payments and stablecoin transfers", "Decentralised trading", "Consumer apps", "Token launches"],
        "learn_more": ["https://solana.com/docs", "https://solana.com/solana-whitepaper.pdf"],
    },
    "XRP": {
        "coingecko_id": "ripple",
        "repo": "XRPLF/rippled",
        "chain": "XRP Ledger",
        "slug": "xrp-ledger",
        "asset": "XRP",
        "launched": "June 2012",
        "purpose": "A ledger built for payments and exchanging currencies quickly and cheaply, with a decentralised exchange built into the ledger itself.",
        "consensus": "The XRP Ledger Consensus Protocol. There is no mining and no staking: validators agree on each ledger version, and each server chooses the validators it trusts (its Unique Node List).",
        "programmability": "Built-in features rather than general smart contracts: payments, issued tokens, a native decentralised exchange, escrow and payment channels.",
        "asset_role": "XRP is the native asset and a bridge currency. 100 billion XRP were created at launch and no more can be made; the small fee on every transaction is destroyed, so the supply only shrinks.",
        "uses": ["Cross-border payments", "Currency exchange on the built-in exchange", "Issued tokens and stablecoins", "Tokenised real-world assets"],
        "learn_more": ["https://xrpl.org/docs", "https://xrpl.org/docs/concepts/consensus-protocol"],
    },
    "BNB": {
        "coingecko_id": "binancecoin",
        "repo": "bnb-chain/bsc",
        "chain": "BNB Chain",
        "slug": "bnb-chain",
        "asset": "BNB",
        "launched": "September 2020 (BNB Smart Chain)",
        "purpose": "A low-fee chain for decentralised apps, compatible with the Ethereum Virtual Machine (EVM, the software that runs Ethereum's smart contracts) and closely tied to the Binance ecosystem.",
        "consensus": "Proof of Staked Authority: a limited set of validators, elected by the BNB staked behind them, take turns producing blocks.",
        "programmability": "EVM-compatible smart contracts, so Ethereum tools and Solidity code work with few changes.",
        "asset_role": "BNB pays fees and is staked to elect validators. BNB is regularly burned (removed from supply) under a published schedule.",
        "uses": ["Low-cost DeFi", "Token launches", "Games and consumer apps"],
        "learn_more": ["https://docs.bnbchain.org/", "https://www.bnbchain.org/en/bnb-smart-chain"],
    },
    "AVAX": {
        "coingecko_id": "avalanche-2",
        "repo": "ava-labs/avalanchego",
        "chain": "Avalanche",
        "slug": "avalanche",
        "asset": "AVAX",
        "launched": "September 2020",
        "purpose": "A network of chains: the main C-Chain runs smart contracts on the Ethereum Virtual Machine (EVM, the software that runs Ethereum's smart contracts), and organisations can launch their own connected chains (called Avalanche L1s, short for layer 1s, and formerly subnets) with their own rules.",
        "consensus": "Proof of stake using the Avalanche family of consensus protocols: validators repeatedly poll small random samples of other validators until they agree, which gives finality in about a second or two.",
        "programmability": "EVM smart contracts on the C-Chain; custom virtual machines on Avalanche L1s.",
        "asset_role": "AVAX pays fees, which are burned, and is staked by validators. The maximum supply is 720 million AVAX.",
        "uses": ["DeFi on the C-Chain", "Institution and game chains as Avalanche L1s", "Tokenised assets"],
        "learn_more": ["https://build.avax.network/docs", "https://www.avax.network/"],
    },
    "HYPE": {
        "coingecko_id": "hyperliquid",
        "repo": "hyperliquid-dex/node",
        "chain": "Hyperliquid",
        "slug": "hyperliquid",
        "asset": "HYPE",
        "launched": "2023 (exchange), November 2024 (HYPE token)",
        "purpose": "A layer 1 blockchain built for trading: its order books for perpetual futures and spot markets run on the chain itself rather than in a company's database.",
        "consensus": "HyperBFT, a proof-of-stake consensus derived from HotStuff, designed for fast finality.",
        "programmability": "Two parts in one chain: HyperCore runs the exchange, and HyperEVM runs smart contracts on the Ethereum Virtual Machine (EVM, the software that runs Ethereum's smart contracts) that can interact with it.",
        "asset_role": "HYPE is staked by validators and pays for gas on HyperEVM. Part of the exchange's fee income has been used to buy HYPE on the market; check the current documentation for how this works today.",
        "uses": ["Perpetual futures trading", "Spot trading", "EVM apps built around the exchange"],
        "learn_more": ["https://hyperliquid.gitbook.io/hyperliquid-docs", "https://hyperliquid.xyz/"],
    },
}

FEATURED = ["BTC", "ETH", "SOL", "XRP", "BNB", "AVAX", "HYPE"]

# Names people type for a featured chain, resolved to its native asset symbol
CHAIN_ALIASES = {
    "BITCOIN": "BTC", "ETHEREUM": "ETH", "SOLANA": "SOL",
    "XRPL": "XRP", "XRP LEDGER": "XRP", "RIPPLE": "XRP",
    "BNB CHAIN": "BNB", "BSC": "BNB", "BINANCE SMART CHAIN": "BNB", "BINANCE": "BNB",
    "AVALANCHE": "AVAX", "HYPERLIQUID": "HYPE",
}


def profile(symbol):
    """The profile for a featured chain's native asset symbol, or None."""
    return PROFILES.get((symbol or "").upper())


def by_slug(slug):
    return next((p for p in PROFILES.values() if p["slug"] == slug), None)
