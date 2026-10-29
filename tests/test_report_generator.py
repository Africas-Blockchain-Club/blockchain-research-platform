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


def test_a_headline_with_advice_words_does_not_block_the_data_report(temp_store, analysis):
    analysis["data_summary"]["recent_news_headlines"] = [
        {"title": "ETH Price Target Raised as Analysts Say Buy", "source": "Example", "published_at": "today"}
    ]
    assert report_generator.save_data_report(analysis)["token"] == "EXM"


def test_a_crafted_ticker_never_reaches_a_url():
    with pytest.raises(ValueError):
        report_generator.fetch_and_analyse("../../evil?x=1")


def test_a_rate_limited_source_is_announced_at_the_top(data_summary):
    from data_analytics.data_report import build_data_report

    data_summary["source_errors"] = {"coingecko": "CoinGecko data endpoint returned 429"}
    text = build_data_report("EXM", data_summary, "19 October 2026")
    assert text.index("Some sources could not be read") < text.index("## Phase 0")
    assert "429" in text


def test_coingecko_waits_and_retries_after_a_rate_limit(monkeypatch):
    from data_engineering import fetchers

    calls = []

    class Resp:
        def __init__(self, code):
            self.status_code, self.headers = code, {"Retry-After": "0"}

    def fake_get(url, headers=None, timeout=None):
        calls.append(url)
        return Resp(429 if len(calls) == 1 else 200)

    monkeypatch.setattr(fetchers.requests, "get", fake_get)
    monkeypatch.setattr(fetchers.time, "sleep", lambda s: None)
    assert fetchers._coingecko_get("https://api.coingecko.com/x", {}).status_code == 200
    assert len(calls) == 2


@pytest.mark.parametrize("query, ok", [("NEAR Protocol", True), ("Shiba-Inu", True), ("TIA", True),
                                       ("../../evil", False), ("SOL?x=1", False), ("", False)])
def test_full_names_pass_and_crafted_input_does_not(query, ok):
    assert report_generator.is_valid_query(query) is ok


def test_a_coin_with_no_pool_is_not_a_failed_source():
    no_pool = {"error": "No exchange pool: no token contract", "no_pool": True}
    errors = report_generator._source_errors(no_pool, {}, {}, {}, {})
    assert errors == {}
    assert "dexscreener" in report_generator._source_errors({"error": "DexScreener returned 500"}, {}, {}, {}, {})
