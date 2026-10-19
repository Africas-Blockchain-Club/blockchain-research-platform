"""
Live staking data for the attack cost calculator, from free public endpoints.

One function per kind of chain. Each returns
  {"staked": coins, "stakes": [coins per validator], "source": str}
or {"error": str}, and never raises. Ethereum and BNB Chain have no free
endpoint small enough to read on every visit (the beacon chain's validator
list is over 300 MB), so the calculator asks for their figure instead.
Every endpoint was checked live on 19 October 2026. Override any of them with
STAKING_API_<SYMBOL>, and switch them all off with STAKING_DATA_ENABLED=false.
"""
import os

import requests

from config import SETTINGS

TIMEOUT = 15
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
AVALANCHE_P_CHAIN = "https://api.avax.network/ext/bc/P"
HYPERLIQUID_INFO = "https://api.hyperliquid.xyz/info"
# Cosmos SDK chains: REST endpoint and the number of decimals in the staking denomination
COSMOS = {
    "TIA": ("Celestia", "https://celestia-rest.publicnode.com", 6),
    "ATOM": ("Cosmos Hub", "https://cosmos-rest.publicnode.com", 6),
}


def _endpoint(symbol, default):
    return os.getenv(f"STAKING_API_{symbol}") or default


def _post(url, body):
    resp = requests.post(url, json=body, timeout=TIMEOUT, headers={"User-Agent": "blockchain-research-platform"})
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and "error" in data:
        raise ConnectionError(str(data["error"])[:200])
    return data


def _result(stakes, source):
    stakes = sorted((s for s in stakes if s > 0), reverse=True)
    if not stakes:
        return {"error": f"{source} returned no validators"}
    return {"staked": sum(stakes), "stakes": stakes, "source": source}


def solana_stake():
    url = _endpoint("SOL", SOLANA_RPC)
    result = _post(url, {"jsonrpc": "2.0", "id": 1, "method": "getVoteAccounts"})["result"]
    # Delinquent validators still hold stake; they count towards the total
    accounts = result["current"] + result["delinquent"]
    return _result([a["activatedStake"] / 1e9 for a in accounts], f"Solana JSON-RPC getVoteAccounts ({url})")


def avalanche_stake():
    url = _endpoint("AVAX", AVALANCHE_P_CHAIN)
    body = {"jsonrpc": "2.0", "id": 1, "method": "platform.getCurrentValidators", "params": {}}
    validators = _post(url, body)["result"]["validators"]
    # Weights are in nAVAX; a validator's weight is its own stake plus its delegators'
    return _result([(int(v["weight"]) + int(v.get("delegatorWeight") or 0)) / 1e9 for v in validators],
                   f"Avalanche P-Chain getCurrentValidators ({url})")


def hyperliquid_stake():
    url = _endpoint("HYPE", HYPERLIQUID_INFO)
    validators = _post(url, {"type": "validatorSummaries"})
    # Stake is in HYPE's smallest unit (8 decimals, from Hyperliquid's spotMeta)
    return _result([int(v["stake"]) / 1e8 for v in validators if v.get("isActive") and not v.get("isJailed")],
                   f"Hyperliquid info API validatorSummaries ({url})")


def cosmos_stake(symbol):
    chain, default_url, decimals = COSMOS[symbol]
    url = _endpoint(symbol, default_url)
    resp = requests.get(f"{url}/cosmos/staking/v1beta1/validators",
                        params={"status": "BOND_STATUS_BONDED", "pagination.limit": 1000},
                        timeout=TIMEOUT, headers={"User-Agent": "blockchain-research-platform"})
    resp.raise_for_status()
    return _result([int(v["tokens"]) / 10 ** decimals for v in resp.json()["validators"]],
                   f"{chain} staking module, bonded validators ({url})")


ADAPTERS = {"SOL": solana_stake, "AVAX": avalanche_stake, "HYPE": hyperliquid_stake,
            **{symbol: (lambda s=symbol: cosmos_stake(s)) for symbol in COSMOS}}


def fetch_staking(symbol):
    """Live staked total and per-validator stakes for a symbol, None when the
    chain has no adapter (or staking data is switched off), or {"error"}."""
    adapter = ADAPTERS.get((symbol or "").upper())
    if not adapter or not SETTINGS.staking_data_enabled:
        return None
    try:
        return adapter()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"[:200]}
