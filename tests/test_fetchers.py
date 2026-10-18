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
