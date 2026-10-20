"""
What it takes to attack a blockchain: the consensus models and the maths.

A proof-of-stake chain is not secure because an attack is impossible. It is
secure because the attack costs more than it can win. These models say what
share of stake each kind of attack needs, with the source for every figure;
where the protocol's documentation gives no single figure (Avalanche), the
model says so and the user sets the share. Proof of work and trusted
validator lists are explained, not priced: buying coins does not attack them.

This is teaching material, never a safety rating: the calculator shows each
chain's own figures and never ranks one chain against another.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Attack:
    share: float  # of all stake, after the attacker's own stake is added
    goal: str
    what_happens: str


@dataclass(frozen=True)
class Model:
    key: str
    label: str
    kind: str  # "stake" is priced; "work" and "trust" are explained
    summary: str
    source: str
    attacks: tuple = field(default_factory=tuple)
    note: str = ""


ETHEREUM = Model(
    "ethereum", "Ethereum proof of stake", "stake",
    "Validators lock ETH as a deposit and vote on blocks. Blocks become final when two thirds of "
    "stake agrees, and stake used to cheat is destroyed (slashed).",
    "https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/attack-and-defense/",
    (
        Attack(1 / 3, "Stall finality",
               "Blocks keep coming, but none becomes final, so exchanges and bridges stop trusting new payments."),
        Attack(1 / 2, "Control which blocks win",
               "Censor transactions and reorder recent blocks."),
        Attack(2 / 3, "Finalise its own history",
               "Make the attacker's version of the chain final without a single honest validator."),
    ),
)

BFT = Model(
    "bft", "BFT proof of stake (CometBFT, HotStuff and similar)", "stake",
    "Validators vote in rounds, and a block is committed when more than two thirds of stake signs it. "
    "Most newer proof-of-stake chains work this way.",
    "https://github.com/cometbft/cometbft/blob/main/spec/consensus/consensus.md",
    (
        Attack(1 / 3, "Halt the chain",
               "Withholding votes stops any block reaching the two thirds it needs, so the chain stops."),
        Attack(2 / 3, "Commit its own blocks",
               "Sign any block the attacker likes, including ones that rewrite recent history."),
    ),
)

SOLANA = Model(
    "solana", "Solana (Tower BFT)", "stake",
    "Validators vote on slots, and a block is final once two thirds of stake has voted for it.",
    "https://solana.com/news/tower-bft--solana-s-high-performance-implementation-of-pbft",
    BFT.attacks,
    note="Solana keeps producing blocks without that two thirds, so a third of stake stalls finality "
         "rather than block production.",
)

HYPERLIQUID = Model(
    "hyperliquid", "Hyperliquid (HyperBFT)", "stake",
    "A HotStuff-style design: a round is committed when validators holding more than two thirds of "
    "stake sign it.",
    "https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/staking",
    BFT.attacks,
)

BNB = Model(
    "bnb", "BNB Chain (Proof of Staked Authority)", "stake",
    "A limited set of validators, elected by the BNB staked behind them, take turns producing blocks. "
    "A block is final once two thirds of validators vote for it.",
    "https://docs.bnbchain.org/bnb-smart-chain/introduction/",
    BFT.attacks,
    note="The finality vote counts validators, not stake, and stake decides who is elected, so pricing "
         "it by stake is an approximation.",
)

AVALANCHE = Model(
    "avalanche", "Avalanche (Snow family sampling)", "stake",
    "Each validator repeatedly asks a small random sample of others, weighted by stake, until it is "
    "confident the network agrees.",
    "https://build.avax.network/academy/avalanche-fundamentals/02-avalanche-consensus-intro/03-snowman-consensus",
    note="Avalanche's documentation gives no single share of stake that breaks it: the answer depends on "
         "the sampling settings and is a probability, not a fixed line. Set the share to explore it.",
)

LONGEST = Model(
    "longest", "Longest-chain proof of stake (Ouroboros and similar)", "stake",
    "Stake decides who may add each block, and the longest valid chain wins, as in proof of work but "
    "with stake in place of computing power. Its security rests on an honest majority of stake.",
    "https://ouroboros-consensus.cardano.intersectmbo.org/docs/references/miscellaneous/cardano_praos_basics",
    (
        Attack(1 / 2, "Control the chain",
               "Add most of the blocks, censor transactions and build a longer chain that reverses recent payments."),
    ),
)

WORK = Model(
    "work", "Proof of work", "work",
    "Miners spend computing power to add blocks, and the chain with the most accumulated work wins. "
    "An attacker needs more than half of the mining power, not coins.",
    "https://bitquery.io/blog/attacker-stole-807k-etc-in-ethereum-classic-51-attack",
)

TRUST = Model(
    "trust", "Trusted validator lists", "trust",
    "There is no mining and no staking. Each server chooses the validators it trusts, and a ledger is "
    "accepted when a supermajority of those trusted validators agrees.",
    "https://xrpl.org/docs/concepts/consensus-protocol",
)

MODELS = {m.key: m for m in (ETHEREUM, BFT, SOLANA, HYPERLIQUID, BNB, AVALANCHE, LONGEST, WORK, TRUST)}

# Chains whose consensus is known; any other chain's user picks the model
CHAIN_MODELS = {
    "BTC": "work", "ETH": "ethereum", "SOL": "solana", "XRP": "trust", "BNB": "bnb",
    "AVAX": "avalanche", "HYPE": "hyperliquid", "TIA": "bft", "ATOM": "bft", "ADA": "longest",
}

# Where to read the staked total when it cannot be fetched live
STAKE_LOOKUP = {
    "ETH": "https://beaconcha.in/",
    "BNB": "https://www.bnbchain.org/en/bnb-staking",
    "ADA": "https://cardanoscan.io/",
}


# Platforms (CoinGecko ids) whose tokens are secured by a chain this page knows
ROLLUPS = {"base": "Base", "arbitrum-one": "Arbitrum One", "optimistic-ethereum": "OP Mainnet",
           "linea": "Linea", "zksync": "zkSync"}
PLATFORM_CHAINS = {"solana": "SOL", "ethereum": "ETH", "binance-smart-chain": "BNB", "avalanche": "AVAX",
                   "hyperevm": "HYPE", "hyperliquid": "HYPE", **{key: "ETH" for key in ROLLUPS}}


def detect(coin, platforms=None):
    """Work out how a coin's chain reaches agreement from CoinGecko's data.

    Returns {"model": key or None, "host": symbol or None, "reason": str}.
    A token that lives on another chain has no consensus of its own, so its
    host chain is the one an attacker would have to beat. Otherwise the
    mining algorithm and CoinGecko's category tags are the clues; "proof of
    stake" alone does not say which kind, so the user is asked."""
    symbol = (coin.get("symbol") or "").upper()
    name = coin.get("name") or symbol
    if symbol in CHAIN_MODELS:
        return {"model": CHAIN_MODELS[symbol], "host": None, "reason": ""}
    platform = coin.get("asset_platform_id")
    platform_info = (platforms or {}).get(platform) or {}
    if platform and platform != coin.get("id") and platform_info.get("native_coin_id") != coin.get("id"):
        host = PLATFORM_CHAINS.get(platform)
        platform_name = platform_info.get("name") or platform
        if not host:
            return {"model": None, "host": None,
                    "reason": f"{name} is a token on {platform_name}, a chain this page has no model for. "
                              f"Choose how {platform_name} reaches agreement."}
        reason = (f"{name} is a token on {platform_name}. It has no consensus of its own: "
                  f"{platform_name}'s validators order its transfers, so an attacker would have to beat "
                  f"{platform_name}.")
        if platform in ROLLUPS:
            reason += (f" {platform_name} is a rollup: it posts its transactions to Ethereum, so its "
                       "history rests on Ethereum's security, while one operator (the sequencer) "
                       "decides the order of transactions.")
        return {"model": CHAIN_MODELS[host], "host": host, "reason": reason}
    tags = coin.get("consensus_tags") or []
    if coin.get("hashing_algorithm") or "Proof of Work (PoW)" in tags:
        algorithm = coin.get("hashing_algorithm")
        clue = f"its mining algorithm ({algorithm})" if algorithm else "its proof-of-work tag"
        return {"model": "work", "host": None, "reason": f"Detected from {clue} on CoinGecko."}
    if "Cosmos Ecosystem" in tags:
        return {"model": "bft", "host": None,
                "reason": "Detected from CoinGecko's Cosmos ecosystem tag: Cosmos chains use CometBFT."}
    if "Proof of Stake (PoS)" in tags:
        return {"model": None, "host": None,
                "reason": f"CoinGecko lists {name} as proof of stake, but not which kind. Choose it from "
                          "the blockchain's documentation."}
    return {"model": None, "host": None, "reason": ""}


def model_for(symbol):
    """The known model for a chain's symbol, or None when the user must choose."""
    key = CHAIN_MODELS.get((symbol or "").upper())
    return MODELS[key] if key else None


def coins_needed(staked, share):
    """Coins an attacker must buy and stake to hold `share` of all stake.

    New stake adds to the total, so holding a third of the result takes half
    of what is staked today, and two thirds takes twice what is staked today:
    x / (staked + x) = share  gives  x = staked * share / (1 - share)."""
    if not 0 < share < 1:
        raise ValueError("share must be between 0 and 1")
    return staked * share / (1 - share)


def fewest_validators(stakes, share):
    """The fewest validators that together hold at least `share` of all stake.
    A small number means an attacker could bribe or compromise a few
    operators instead of buying anything."""
    total = sum(stakes)
    if total <= 0:
        return None
    held = 0.0
    for count, stake in enumerate(sorted(stakes, reverse=True), start=1):
        held += stake
        if held >= share * total:
            return count
    return len(stakes)


def price_attack(staked, share, price_usd, circulating=None, volume_24h_usd=None):
    """The figures for one attack. Every value is a plain measurement:
    the coins and dollars needed, and how they compare with the coins that
    exist and with a day of trading."""
    coins = coins_needed(staked, share)
    cost = coins * price_usd
    unstaked = (circulating - staked) if circulating and circulating > staked else None
    return {
        "coins": coins,
        "cost_usd": cost,
        # Share of the coins in circulation that are not already staked: above 1,
        # there are not enough coins on the market to buy
        "share_of_unstaked": coins / unstaked if unstaked else None,
        "days_of_volume": cost / volume_24h_usd if volume_24h_usd else None,
    }
