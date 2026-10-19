import pytest

from data_analytics.data_report import build_data_report, sell_price_impact
from data_science.compliance import find_advice_language


def test_sell_price_impact_matches_constant_product():
    # Selling as many tokens as the pool holds doubles x, so price falls to a quarter
    assert sell_price_impact(1_000, 1.0, 1_000) == pytest.approx(0.75)
    assert sell_price_impact(None, 1.0, 1_000) is None
    assert sell_price_impact(1_000, 0, 1_000) is None


def test_data_report_has_every_phase_and_no_advice(data_summary):
    text = build_data_report("EXM", data_summary, "18 October 2026")
    for heading in ("## Phase 0", "## Phase 1:", "## Phase 1.5", "## Phase 2:", "## Phase 2.5", "## Phase 3", "## Phase 4"):
        assert heading in text
    assert find_advice_language(text) == []


def test_data_report_shows_rand_alongside_dollars(data_summary):
    text = build_data_report("EXM", data_summary, "18 October 2026")
    assert "$1,000,000,000 (R17,500,000,000)" in text


def test_data_report_survives_an_empty_summary():
    text = build_data_report("EXM", {}, "18 October 2026")
    assert "N/A" in text
    assert "could not be read" in text.lower()


def test_order_book_market_is_explained_not_shown_as_empty(data_summary):
    info = data_summary["token_info"]
    info.update(liquidity_usd=None, liquidity_base_tokens=None, liquidity_quote_tokens=None,
                liquidity_reported=False)
    report = build_data_report("HYPE", data_summary, "19 October 2026")
    assert "order book" in report
    assert "No data (not reported)" in report
