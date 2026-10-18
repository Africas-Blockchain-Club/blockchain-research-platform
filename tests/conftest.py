import os
import sys
from pathlib import Path

# Tests never call a real model or spend money, whatever is in .env
os.environ["AI_ENABLED"] = "false"
os.environ["PAYMENTS_ENABLED"] = "false"
os.environ["SCREENSHOTS_ENABLED"] = "false"
# Tests build the site explicitly where they need it
os.environ["SITE_BUILD_ON_SAVE"] = "false"

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402


@pytest.fixture
def data_summary():
    """A realistic free-stage summary with no network calls."""
    return {
        "fx": {"usd_zar": 17.5, "source": "test"},
        "token_info": {
            "name": "Example",
            "symbol": "EXM",
            "chain": "ethereum",
            "dex": "uniswap",
            "dex_pair_match": "contract address published by CoinGecko",
            "current_price_usd": 2.0,
            "market_cap_usd": 1_000_000_000,
            "fully_diluted_valuation_usd": 4_000_000_000,
            "24h_change_pct": -1.2,
            "7d_change_pct": 3.4,
            "30d_change_pct": -40.0,
            "ath_usd": 10.0,
            "ath_change_pct": -80.0,
            "total_supply": 2_000_000_000,
            "circulating_supply": 500_000_000,
            "max_supply": 2_000_000_000,
            "24h_volume_dex_pair_usd": 1_000_000,
            "24h_volume_total_all_exchanges_usd": 50_000_000,
            "liquidity_usd": 5_000_000,
            "liquidity_base_tokens": 1_250_000,
            "liquidity_quote_tokens": 2_500_000,
        },
        "community_and_social": {"token_description": "An example token.", "token_categories": ["DeFi"]},
        "recent_news_headlines": [{"title": "Example ships an upgrade", "source": "Test", "published_at": "today"}],
        "listing_status": {"listed_on_coingecko": True, "listed_on_coinmarketcap": None},
        "protocol_analytics": {"kind": "protocol", "name": "Example", "tvl_usd": 12_000_000, "match": "protocol name"},
        "derivatives_data": {"error": "COINGLASS_API_KEY not set"},
    }


@pytest.fixture
def temp_store(tmp_path, monkeypatch):
    """Point the report store and the database at a temporary folder."""
    from sqlalchemy import create_engine

    import db
    from tools import report_store

    monkeypatch.setattr(report_store, "REPORTS_DIR", tmp_path / "reports")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    db.metadata.create_all(engine)
    monkeypatch.setattr(db, "_engine", engine)
    return tmp_path / "reports"
