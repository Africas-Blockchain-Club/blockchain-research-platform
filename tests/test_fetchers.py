from data_engineering.fetchers import _deepest_active, token_contracts


def test_native_coins_use_their_wrapped_contract():
    assert token_contracts("sol") == [("solana", "So11111111111111111111111111111111111111112")]


def test_coingecko_platform_names_map_to_dexscreener_chains():
    contracts = token_contracts("ENA", {"ethereum": "0xabc", "binance-smart-chain": "0xdef"})
    assert ("bsc", "0xdef") in contracts
    assert ("ethereum", "0xabc") in contracts


def test_idle_pools_lose_to_active_ones():
    idle = {"liquidity": {"usd": 2_500_000_000}, "volume": {"h24": 0}}
    active = {"liquidity": {"usd": 28_000_000}, "volume": {"h24": 9_000_000}}
    assert _deepest_active([idle, active]) is active
