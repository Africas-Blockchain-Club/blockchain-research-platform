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


def test_unconnected_sources_are_no_data(data_summary):
    checks = _by_key(compute_risk_checks(data_summary))
    for key in ("unlock_schedule", "holder_concentration", "leverage"):
        assert checks[key]["status"] == NO_DATA


def test_counts_are_counts_not_a_score(data_summary):
    checks = compute_risk_checks(data_summary)
    counts = summarise_checks(checks)
    assert sum(counts.values()) == len(checks) == 10
    assert all("score" not in check for check in checks)


def test_markdown_section_explains_no_data(data_summary):
    text = risk_checks_markdown(compute_risk_checks(data_summary))
    assert text.startswith("## Risk Checks")
    assert "not the same as clear" in text
