import pytest

from data_analytics.risk_profile import compute_risk_checks
from data_science.ai_generator import REQUIRED_HEADINGS
from data_science.compliance import AdviceLanguageError
from data_science.llm import AIResponseError
from tools import report_generator, report_store

GOOD_BODY = "# EXM Research Report\n\n" + "\n\n".join(f"{h}: Section\n\nA fact." for h in REQUIRED_HEADINGS)


@pytest.fixture
def analysis(data_summary):
    return {
        "token": "EXM",
        "data_summary": data_summary,
        "risk_checks": compute_risk_checks(data_summary),
        "screenshot_path": None,
    }


def _fake_ai(text):
    return lambda *args, **kwargs: {"text": text, "model": "test-model", "cost_usd": 0.01,
                                    "input_tokens": 1, "output_tokens": 1}


@pytest.mark.parametrize("name, ticker", [("solana", "SOL"), (" Ethereum ", "ETH"), ("matic", "POL"), ("ena", "ENA")])
def test_normalise_token(name, ticker):
    assert report_generator.normalise_token(name) == ticker


def test_data_report_saves_without_ai(temp_store, analysis):
    meta = report_generator.save_data_report(analysis)
    assert meta["mode"] == report_store.MODE_DATA
    assert meta["model"] is None


def test_ai_report_saves_when_clean(temp_store, analysis, monkeypatch):
    monkeypatch.setattr(report_generator, "generate_ai_report", _fake_ai(GOOD_BODY))
    meta = report_generator.save_ai_report(analysis)
    assert meta["mode"] == report_store.MODE_AI
    assert meta["model"] == "test-model"


def test_ai_report_with_advice_is_rejected_and_not_saved(temp_store, analysis, monkeypatch):
    monkeypatch.setattr(report_generator, "generate_ai_report", _fake_ai(GOOD_BODY + "\n\nRating: Strong Buy"))
    with pytest.raises(AdviceLanguageError):
        report_generator.save_ai_report(analysis)
    assert report_store.list_reports() == []


def test_ai_report_missing_sections_is_rejected(temp_store, analysis, monkeypatch):
    monkeypatch.setattr(report_generator, "generate_ai_report", _fake_ai("# EXM\n\n## Phase 0: Only"))
    with pytest.raises(AIResponseError):
        report_generator.save_ai_report(analysis)
    assert report_store.list_reports() == []
