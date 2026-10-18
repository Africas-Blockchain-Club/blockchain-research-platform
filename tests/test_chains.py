import pytest

from data_analytics import chains
from data_analytics.data_report import build_data_report
from data_engineering import networks
from tools.report_generator import normalise_token

FIELDS = ("chain", "slug", "asset", "repo", "launched", "purpose", "consensus", "programmability", "asset_role", "uses", "learn_more")


@pytest.mark.parametrize("symbol", chains.FEATURED)
def test_every_featured_chain_has_a_complete_profile(symbol):
    profile = chains.profile(symbol)
    for field in FIELDS:
        assert profile.get(field), f"{symbol} is missing {field}"
    assert all(url.startswith("https://") for url in profile["learn_more"])


def test_the_seven_featured_chains():
    assert chains.FEATURED == ["BTC", "ETH", "SOL", "XRP", "BNB", "AVAX", "HYPE"]


@pytest.mark.parametrize("typed, symbol", [
    ("Bitcoin", "BTC"), ("solana", "SOL"), ("XRP Ledger", "XRP"), ("xrpl", "XRP"),
    ("BNB Chain", "BNB"), ("avalanche", "AVAX"), ("Hyperliquid", "HYPE"), ("  ethereum ", "ETH"),
])
def test_chain_names_resolve_to_their_native_asset(typed, symbol):
    assert normalise_token(typed) == symbol


def test_every_featured_chain_has_a_network_adapter():
    for symbol in chains.FEATURED:
        assert symbol in ("BTC", "SOL", "XRP") or symbol in networks.EVM


def test_evm_adapter_measures_block_time(monkeypatch):
    blocks = {"latest": {"number": hex(1000), "timestamp": hex(2000), "transactions": ["a", "b"]},
              hex(900): {"number": hex(900), "timestamp": hex(800)}}

    def fake_rpc(url, method, params=None, xrpl=False):
        if method == "eth_chainId":
            return hex(1)
        if method == "eth_gasPrice":
            return hex(2_000_000_000)
        return blocks[params[0]]

    monkeypatch.setattr(networks, "_rpc", fake_rpc)
    result = networks.evm_network("ETH")
    values = {m["name"]: m["value"] for m in result["metrics"]}
    assert values["Average block time"] == "12.00 seconds"
    assert values["Gas price"] == "2.0000 gwei"


def test_an_unreachable_network_is_reported_not_raised(monkeypatch):
    def broken(*args, **kwargs):
        raise ConnectionError("down")

    monkeypatch.setattr(networks, "_rpc", broken)
    result = networks.xrpl_network()
    assert result["metrics"] == [] and "down" in result["error"]


def test_the_report_leads_with_the_blockchain(data_summary):
    data_summary["blockchain"] = {"profile": chains.profile("XRP"), "network": {
        "chain": "XRP Ledger", "source": "test", "metrics": [{"name": "Validators", "value": "35", "meaning": "m"}]}}
    text = build_data_report("XRP", data_summary, "18 October 2026")
    assert text.startswith("# XRP Ledger (XRP) Blockchain Research Report")
    assert text.index("## Phase 0: The Blockchain") < text.index("## Phase 1: The Native Asset")
    assert "Unique Node List" in text and "| Validators | 35 |" in text
