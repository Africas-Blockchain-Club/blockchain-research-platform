"""The research page's shared data cache, run in Streamlit's own test runner."""
from streamlit.testing.v1 import AppTest


def _two_fetches():
    # Runs as a Streamlit script: two visitors fetch the same coin within the cache time
    from unittest import mock

    import streamlit as st

    from dashboards.views import research

    def fake_fetch(token, log_fn=None):
        log_fn("Reading the market data...")
        return {"token": token, "data_summary": {}, "risk_checks": []}

    st.cache_data.clear()
    with mock.patch.object(research, "fetch_and_analyse", fake_fetch), \
            mock.patch.object(research, "count_search", lambda *a, **k: None):
        research._fetch("EXM")
        st.session_state.pop("analysis")
        research._fetch("EXM")


def test_a_repeat_fetch_is_served_from_the_cache():
    # A cache hit replayed the progress lines into a box made outside the cached
    # function, which Streamlit refuses: the second visitor got an error instead of data
    at = AppTest.from_function(_two_fetches).run(timeout=30)
    assert not at.exception
    assert not at.error, [e.value for e in at.error]
    assert at.session_state["analysis"]["token"] == "EXM"
    assert [s.label for s in at.status] == ["Data for EXM is ready"] * 2


def _monitor_fetch():
    from unittest import mock

    import streamlit as st

    from dashboards.views import research

    st.session_state["counted"] = []
    fake = mock.MagicMock(headers={"User-Agent": "Mozilla/5.0 HeadlessChrome BRP-monitor"})
    with mock.patch.object(research, "fetch_and_analyse",
                           lambda token, log_fn=None: {"token": token, "data_summary": {}, "risk_checks": []}), \
            mock.patch.object(research.st, "context", fake), \
            mock.patch.object(research, "count_search", lambda *a, **k: st.session_state["counted"].append(a)):
        research._fetch("EXN")


def test_the_monitor_is_not_counted_as_a_search():
    at = AppTest.from_function(_monitor_fetch).run(timeout=30)
    assert not at.exception
    assert at.session_state["counted"] == []
