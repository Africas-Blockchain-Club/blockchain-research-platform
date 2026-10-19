from data_analytics.risk_profile import (
    CLEAR,
    FLAGGED,
    NO_DATA,
    compute_risk_checks,
    risk_checks_markdown,
    summarise_checks,
)


def _by_key(checks):
    return {check["key"]: check for check in checks}


def test_checks_flag_and_clear_on_thresholds(data_summary):
    checks = _by_key(compute_risk_checks(data_summary))
    assert checks["dilution"]["status"] == FLAGGED  # FDV 4x market cap
    assert checks["low_float"]["status"] == FLAGGED  # 25% circulating
    assert checks["drawdown"]["status"] == FLAGGED  # -80%
    assert checks["volatility"]["status"] == FLAGGED  # -40% in 30 days
    assert checks["thin_liquidity"]["status"] == FLAGGED  # 0.5% of market cap
    assert checks["artificial_volume"]["status"] == CLEAR  # 5% turnover
    assert checks["listing_coverage"]["status"] == CLEAR


def test_missing_data_is_never_clear():
    checks = compute_risk_checks({})
    assert {check["status"] for check in checks} == {NO_DATA}


def test_listing_outage_is_no_data_not_flagged(data_summary):
    data_summary["listing_status"] = {"listed_on_coingecko": None, "listed_on_coinmarketcap": None}
    assert _by_key(compute_risk_checks(data_summary))["listing_coverage"]["status"] == NO_DATA


def test_leverage_without_futures_data_is_no_data(data_summary):
    assert _by_key(compute_risk_checks(data_summary))["leverage"]["status"] == NO_DATA


def test_leverage_uses_open_interest_from_the_venues(data_summary):
    # Market cap in the fixture is 1 billion; 150 million open interest is 15%
    data_summary["derivatives_data"] = {"open_interest": 150_000_000, "venues": {"Binance": 150_000_000},
                                        "failed": {}, "source": "test venues"}
    check = _by_key(compute_risk_checks(data_summary))["leverage"]
    assert check["status"] == FLAGGED
    assert check["source"] == "test venues"


def test_no_futures_market_anywhere_is_clear_not_missing(data_summary):
    data_summary["derivatives_data"] = {"venues": {}, "not_listed": ["Binance"], "failed": {}, "error": "none"}
    assert _by_key(compute_risk_checks(data_summary))["leverage"]["status"] == CLEAR


def test_a_failed_venue_is_never_read_as_no_market(data_summary):
    data_summary["derivatives_data"] = {"venues": {}, "failed": {"Binance": "timeout"}, "error": "failed"}
    assert _by_key(compute_risk_checks(data_summary))["leverage"]["status"] == NO_DATA


def test_exchange_depth_replaces_the_dex_pool_for_liquidity(data_summary):
    data_summary["market_depth"] = {"depth_down_2pct_usd": 50_000_000, "markets_counted": 12}
    check = _by_key(compute_risk_checks(data_summary))["thin_liquidity"]
    assert check["status"] == CLEAR
    assert check["name"] == "Thin market depth"
    data_summary["market_depth"] = {"depth_down_2pct_usd": 400_000, "markets_counted": 3}
    assert _by_key(compute_risk_checks(data_summary))["thin_liquidity"]["status"] == FLAGGED


def test_unmeasurable_topics_are_listed_not_counted(data_summary):
    checks = _by_key(compute_risk_checks(data_summary))
    assert "unlock_schedule" not in checks and "holder_concentration" not in checks
    text = risk_checks_markdown(list(checks.values()))
    assert "Not covered by these checks" in text
    assert "Token unlocks" in text and "top-holders" in text


def test_counts_are_counts_not_a_score(data_summary):
    checks = compute_risk_checks(data_summary)
    counts = summarise_checks(checks)
    assert sum(counts.values()) == len(checks) == 8
    assert all("score" not in check for check in checks)


def test_markdown_section_explains_no_data(data_summary):
    text = risk_checks_markdown(compute_risk_checks(data_summary))
    assert text.startswith("## Risk Checks")
    assert "not the same as clear" in text
