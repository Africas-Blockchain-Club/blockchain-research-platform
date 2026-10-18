"""
Live network data for the featured blockchains, from free public endpoints.

One function per kind of chain. Each returns
  {"chain", "source", "metrics": [{"name", "value", "meaning"}], "error"?}
and never raises: a failed endpoint becomes a labelled error that the report
shows as "No data", so an outage can never read as a healthy network.
Every endpoint was checked live on 18 October 2026. Override any of them
with NETWORK_RPC_<SYMBOL>, for example NETWORK_RPC_ETH=https://...
"""
import os

import requests

TIMEOUT = 12
BLOCK_SAMPLE = 100  # blocks used to measure the average block time on EVM chains

EVM = {
    "ETH": ("Ethereum", "https://ethereum-rpc.publicnode.com", 1),
    "BNB": ("BNB Chain", "https://bsc-dataseed.bnbchain.org", 56),
    "AVAX": ("Avalanche C-Chain", "https://api.avax.network/ext/bc/C/rpc", 43114),
    "HYPE": ("Hyperliquid (HyperEVM)", "https://rpc.hyperliquid.xyz/evm", 999),
}
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
XRPL_RPC = "https://xrplcluster.com/"
MEMPOOL = "https://mempool.space/api"


def _endpoint(symbol, default):
    return os.getenv(f"NETWORK_RPC_{symbol}") or default


def _rpc(url, method, params=None, xrpl=False):
    body = {"method": method, "params": params or [{}]} if xrpl else {
        "jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
    resp = requests.post(url, json=body, timeout=TIMEOUT, headers={"User-Agent": "blockchain-research-platform"})
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise ConnectionError(f"{method}: {data['error']}")
    return data["result"]


def _metric(name, value, meaning):
    return {"name": name, "value": value, "meaning": meaning}


def _failed(chain, source, error):
    return {"chain": chain, "source": source, "metrics": [], "error": f"{type(error).__name__}: {error}"[:200]}


def evm_network(symbol):
    chain, default_url, chain_id = EVM[symbol]
    url = _endpoint(symbol, default_url)
    try:
        if int(_rpc(url, "eth_chainId"), 16) != chain_id:
            raise ConnectionError(f"endpoint is not chain {chain_id}")
        latest = _rpc(url, "eth_getBlockByNumber", ["latest", False])
        height = int(latest["number"], 16)
        older = _rpc(url, "eth_getBlockByNumber", [hex(height - BLOCK_SAMPLE), False])
        block_time = (int(latest["timestamp"], 16) - int(older["timestamp"], 16)) / BLOCK_SAMPLE
        gas_gwei = int(_rpc(url, "eth_gasPrice"), 16) / 1e9
        txs = len(latest.get("transactions") or [])
        return {
            "chain": chain,
            "source": f"Public JSON-RPC endpoint ({url})",
            "metrics": [
                _metric("Latest block", f"{height:,}", "How many blocks the chain has produced; it should keep rising."),
                _metric("Average block time", f"{block_time:.2f} seconds",
                        f"Measured over the last {BLOCK_SAMPLE} blocks: how often new transactions are confirmed."),
                _metric("Gas price", f"{gas_gwei:,.4f} gwei",
                        "The price per unit of computation (1 gwei is a billionth of the native coin). Higher means busier or more expensive."),
                _metric("Transactions in the latest block", f"{txs:,}", "A rough sign of how busy the chain is right now."),
            ],
        }
    except Exception as e:
        return _failed(chain, url, e)


def bitcoin_network():
    try:
        get = lambda path: requests.get(f"{MEMPOOL}{path}", timeout=TIMEOUT,  # noqa: E731
                                        headers={"User-Agent": "blockchain-research-platform"})
        height = int(get("/blocks/tip/height").text)
        fees = get("/v1/fees/recommended").json()
        hashrate = get("/v1/mining/hashrate/3d").json().get("currentHashrate") or 0
        return {
            "chain": "Bitcoin",
            "source": "mempool.space public API",
            "metrics": [
                _metric("Latest block", f"{height:,}", "Bitcoin adds a block about every ten minutes."),
                _metric("Fee for next-block confirmation", f"{fees.get('fastestFee')} sat/vB",
                        "Satoshis (a hundred-millionth of a bitcoin) per virtual byte of transaction data."),
                _metric("Fee for confirmation within an hour", f"{fees.get('hourFee')} sat/vB",
                        "What patient senders pay; the gap to the fastest fee shows how congested the network is."),
                _metric("Hash rate", f"{hashrate / 1e18:,.0f} EH/s",
                        "Exahashes per second: the computing power securing the chain. More hash rate makes an attack costlier."),
            ],
        }
    except Exception as e:
        return _failed("Bitcoin", MEMPOOL, e)


def solana_network():
    url = _endpoint("SOL", SOLANA_RPC)
    try:
        samples = _rpc(url, "getRecentPerformanceSamples", [10])
        seconds = sum(s["samplePeriodSecs"] for s in samples)
        total = sum(s["numTransactions"] for s in samples) / seconds
        non_vote = sum(s.get("numNonVoteTransactions", 0) for s in samples) / seconds
        slot_time = seconds / sum(s["numSlots"] for s in samples)
        epoch = _rpc(url, "getEpochInfo")
        return {
            "chain": "Solana",
            "source": f"Public JSON-RPC endpoint ({url})",
            "metrics": [
                _metric("Transactions per second (all)", f"{total:,.0f}",
                        "Includes validators' own vote transactions, which make up most of Solana's traffic."),
                _metric("Transactions per second (users)", f"{non_vote:,.0f}",
                        "Non-vote transactions only: the activity people and programs actually create."),
                _metric("Average slot time", f"{slot_time:.3f} seconds", "How often a validator gets the chance to add a block."),
                _metric("Current epoch", f"{epoch['epoch']:,}", "Epochs are the periods after which stake and rewards are recalculated."),
            ],
        }
    except Exception as e:
        return _failed("Solana", url, e)


def xrpl_network():
    url = _endpoint("XRP", XRPL_RPC)
    try:
        info = _rpc(url, "server_info", xrpl=True)["info"]
        ledger = info["validated_ledger"]
        close = info.get("last_close", {})
        return {
            "chain": "XRP Ledger",
            "source": f"Public XRP Ledger server ({url})",
            "metrics": [
                _metric("Latest validated ledger", f"{ledger['seq']:,}", "The XRP Ledger closes a new ledger version every few seconds."),
                _metric("Time to reach agreement", f"{close.get('converge_time_s', 0):.2f} seconds",
                        "How long the validators took to agree on the last ledger."),
                _metric("Validators in the last round", f"{close.get('proposers', 0):,}",
                        "Validators that proposed in the last consensus round: a direct measure of how many parties agreed."),
                _metric("Base transaction fee", f"{ledger['base_fee_xrp']:.6f} XRP", "This fee is destroyed, not paid to anyone."),
            ],
        }
    except Exception as e:
        return _failed("XRP Ledger", url, e)


def fetch_network(symbol):
    """Live network data for a featured chain's native asset symbol, or None
    for a chain without a network adapter yet."""
    symbol = (symbol or "").upper()
    if symbol == "BTC":
        return bitcoin_network()
    if symbol == "SOL":
        return solana_network()
    if symbol == "XRP":
        return xrpl_network()
    if symbol in EVM:
        return evm_network(symbol)
    return None
