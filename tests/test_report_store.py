import pytest

from data_analytics.risk_profile import compute_risk_checks
from tools import report_store


def _save(data_summary, body="# EXM Research Report\n\n## Phase 0: Overview\n\nText.\n"):
    return report_store.save_report(
        "exm", body, mode=report_store.MODE_DATA, model=None,
        risk_checks=compute_risk_checks(data_summary), data_summary=data_summary,
    )


def test_save_list_and_load(temp_store, data_summary):
    meta = _save(data_summary)
    assert meta["token"] == "EXM"
    assert [m["token"] for m in report_store.list_reports()] == ["EXM"]
    loaded_meta, markdown = report_store.load_report("EXM")
    assert loaded_meta["flagged"] == meta["flagged"]
    assert not markdown.startswith("---")


def test_disclaimer_follows_the_title_and_code_owned_sections_close_it(temp_store, data_summary):
    _save(data_summary)
    _, markdown = report_store.load_report("EXM")
    lines = markdown.splitlines()
    assert lines[0].startswith("# EXM")
    assert "not financial advice" in lines[2]
    assert "## Risk Checks" in markdown
    assert markdown.rstrip().endswith("No AI wrote any part of it.")


@pytest.mark.parametrize("token", ["../etc", "SOL/../x", "", "a b"])
def test_tokens_that_could_escape_the_folder_are_rejected(token):
    assert not report_store.is_valid_token(token)
    with pytest.raises(ValueError):
        report_store._paths(token)


def test_split_sections():
    sections = report_store.split_sections("# T\n\nIntro\n\n## Phase 0: A\nOne\n## Phase 1: B\nTwo\n")
    assert [title for title, _ in sections] == ["Introduction", "Phase 0: A", "Phase 1: B"]


def test_old_format_reports_are_ignored(temp_store):
    temp_store.mkdir(parents=True, exist_ok=True)
    (temp_store / "OLD_research_report.json").write_text('{"format": 2, "token": "OLD"}')
    assert report_store.list_reports() == []


def test_a_payment_counts_as_delivered_once_its_report_exists(temp_store, data_summary):
    import db

    payment_id = db.record_payment_attempt(
        request_id="r", token_symbol="EXM", payer_address="0xp", recipient_address="0xr", chain_id=8453,
        asset_contract="0xu", asset_symbol="USDC", amount_atomic=2_000_000, amount_decimal=2, tx_hash="0xabc",
    )
    assert not db.report_exists_for_payment(payment_id)
    report_store.save_report(
        "EXM", "# EXM\n", mode=report_store.MODE_AI, model="m",
        risk_checks=compute_risk_checks(data_summary), data_summary=data_summary, payment_id=payment_id,
    )
    assert db.report_exists_for_payment(payment_id)


def test_payments_report_runs_on_an_empty_and_a_used_database(temp_store, data_summary, capsys):
    import db
    from scripts import payments_report

    payments_report.main()
    assert "No payments recorded yet" in capsys.readouterr().out
    db.record_payment_attempt(
        request_id="r", token_symbol="EXM", payer_address="0xp", recipient_address="0xr", chain_id=8453,
        asset_contract="0xu", asset_symbol="USDT", amount_atomic=2_000_000, amount_decimal=2, tx_hash="0xdef",
    )
    payments_report.main()
    assert "NO REPORT" in capsys.readouterr().out


def test_searches_are_counted_and_ranked(tmp_path, monkeypatch):
    import db

    monkeypatch.setattr(db, "_engine", None)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    for symbol, name in (("TIA", "Celestia"), ("ADA", "Cardano"), ("TIA", "Celestia")):
        db.record_search(symbol, "research", name)
    rows = db.search_summary(days=30)
    assert [(r["token"], r["name"], r["searches"]) for r in rows] == [("TIA", "Celestia", 2), ("ADA", "Cardano", 1)]
    assert db.count_ai_write_ups() == 0
    monkeypatch.setattr(db, "_engine", None)
