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
