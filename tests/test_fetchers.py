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


class FakeResponse:
    def __init__(self, body):
        self.content = body.encode()

    def raise_for_status(self):
        pass


FEED = """<?xml version="1.0"?><rss><channel>
<item><title>Ledger upgrade ships &amp; validators agree - Example News</title><pubDate>Sun, 18 Oct 2026 10:00:00 GMT</pubDate></item>
<item><title>Second story - Other Desk</title><pubDate>Sun, 18 Oct 2026 12:00:00 GMT</pubDate></item>
</channel></rss>"""

BOMB = """<?xml version="1.0"?><!DOCTYPE r [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">]>
<rss><channel><item><title>&b;</title></item></channel></rss>"""


def test_news_feed_is_parsed_and_sorted(monkeypatch):
    from data_engineering import fetchers

    monkeypatch.setattr(fetchers.requests, "get", lambda *a, **k: FakeResponse(FEED))
    headlines = fetchers.fetch_cryptopanic_news("XRP")
    assert headlines[0] == {"title": "Second story", "source": "Other Desk", "published_at": "Sun, 18 Oct 2026 12:00:00 GMT"}
    assert headlines[1]["title"] == "Ledger upgrade ships & validators agree"


def test_entity_expansion_in_a_feed_is_refused(monkeypatch):
    from data_engineering import fetchers

    monkeypatch.setattr(fetchers.requests, "get", lambda *a, **k: FakeResponse(BOMB))
    assert "error" in fetchers.fetch_cryptopanic_news("XRP")[0]


def test_order_book_market_reports_missing_liquidity_not_zero():
    # DexScreener's Hyperliquid spot pair, 19 October 2026: volume, no liquidity object
    from data_analytics.metrics import compute_derived_metrics
    from data_engineering.fetchers import _pair_summary

    pair = {"dexId": "hyperliquid", "chainId": "hyperliquid", "priceUsd": "77.47",
            "volume": {"h24": 39_849_102}, "baseToken": {"symbol": "HYPE"}}
    summary = _pair_summary(pair, "contract address published by CoinGecko")
    assert summary["liquidity_usd"] is None
    assert summary["liquidity_reported"] is False
    metrics = compute_derived_metrics(summary, "HYPE")
    assert metrics["liquidity_usd"] is None
    assert metrics["depth_to_mcap_ratio"] is None


def test_open_interest_separates_not_listed_from_failed(monkeypatch):
    from data_engineering import derivatives

    def listed(_symbol):
        return 1_000_000.0

    def not_listed(_symbol):
        raise derivatives.NotListed("no contract")

    def down(_symbol):
        raise ConnectionError("timeout")

    monkeypatch.setattr(derivatives, "RETRY_SECONDS", 0)
    monkeypatch.setattr(derivatives, "VENUES", (("A", listed), ("B", not_listed), ("C", down)))
    result = derivatives.fetch_open_interest("ETH")
    assert result["open_interest"] == 1_000_000.0
    assert result["not_listed"] == ["B"]
    assert list(result["failed"]) == ["C"]

    monkeypatch.setattr(derivatives, "VENUES", (("B", not_listed),))
    assert "No perpetual futures market" in derivatives.fetch_open_interest("ZZZ")["error"]


def test_market_depth_counts_only_large_exchanges(monkeypatch):
    from data_engineering import fetchers

    class Resp:
        status_code = 200

        def json(self):
            return {"tickers": [
                {"market": {"identifier": "binance", "name": "Binance"}, "base": "ETH", "target": "USDT",
                 "cost_to_move_down_usd": 10_000_000, "cost_to_move_up_usd": 9_000_000},
                {"market": {"identifier": "tiny-exchange", "name": "Tiny"}, "base": "ETH", "target": "USDT",
                 "cost_to_move_down_usd": 900_000_000, "cost_to_move_up_usd": 900_000_000},
            ]}

    monkeypatch.setattr(fetchers, "_coingecko_get", lambda *_a, **_k: Resp())
    depth = fetchers.fetch_market_depth("ethereum")
    assert depth["depth_down_2pct_usd"] == 10_000_000
    assert depth["markets_counted"] == 1


def test_a_venue_that_drops_once_is_retried(monkeypatch):
    from data_engineering import derivatives

    calls = []

    def flaky(_symbol):
        calls.append(1)
        if len(calls) == 1:
            raise ConnectionError("dropped")
        return 5.0

    monkeypatch.setattr(derivatives, "RETRY_SECONDS", 0)
    monkeypatch.setattr(derivatives, "VENUES", (("A", flaky),))
    result = derivatives.fetch_open_interest("BTC")
    assert result["venues"] == {"A": 5.0}
    assert result["failed"] == {}


def test_a_full_name_finds_its_coin_and_an_impostor_loses_on_rank():
    from data_engineering.fetchers import _best_search_match

    coins = [
        {"id": "celestia-fake", "name": "Celestia", "symbol": "CEL2", "market_cap_rank": None},
        {"id": "celestia", "name": "Celestia", "symbol": "TIA", "market_cap_rank": 102},
    ]
    assert _best_search_match(coins, "CELESTIA")["symbol"] == "TIA"
    assert _best_search_match(coins, "tia")["id"] == "celestia"
    assert _best_search_match(coins, "Celest") is None
