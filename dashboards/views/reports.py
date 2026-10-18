"""Reports: the library, and one report at a time when ?token= is set."""
import streamlit as st

from config import ROOT_DIR
from dashboards.ui.components import (
    disclaimer_notice,
    generated_label,
    mode_pill,
    page_header,
    report_card_html,
    risk_cards,
    stat_tiles,
)
from dashboards.ui.pdf import markdown_to_pdf
from data_analytics.risk_profile import summarise_checks
from tools import report_store


def _for_display(text):
    """Escape dollar signs so Streamlit does not read them as maths, and swap
    any long dashes that slipped through for hyphens."""
    return text.replace("\u2014", "-").replace("\u2013", "-").replace("$", r"\$")


def _library():
    page_header("Reports", "Research reports", "Every report saved on this copy of the platform, newest first.")
    disclaimer_notice()
    reports = report_store.list_reports()
    if not reports:
        st.info("No reports yet. Use Research a token to create one.")
        return
    cards = "".join(report_card_html(meta, f"reports?token={meta['token']}") for meta in reports)
    st.html(f'<div class="brp-grid three">{cards}</div>')


def _report(token):
    loaded = report_store.load_report(token)
    if loaded is None:
        st.error(f"There is no report for {token}. Pick one from the list, or research the token first.")
        if st.button("Show all reports"):
            st.query_params.clear()
            st.rerun()
        return
    meta, markdown = loaded

    if st.button("Back to all reports"):
        st.query_params.clear()
        st.rerun()

    page_header("Research report", f"{meta.get('name') or token} ({token})", f"Data from {generated_label(meta)}")
    st.html(mode_pill(meta))
    disclaimer_notice()
    stat_tiles(summarise_checks(meta["risk_checks"]))

    sections = [(title, text) for title, text in report_store.split_sections(markdown)
                if title not in ("Introduction", "Risk Checks")]
    tab_names = ["Risk checks"] + [title for title, _ in sections] + ["Download"]
    tabs = st.tabs(tab_names, default="Risk checks")

    with tabs[0]:
        st.caption(
            "Each check compares one number with a teaching threshold. No data means the platform "
            "could not measure it, not that the risk is absent. The checks are never added into a score."
        )
        risk_cards(meta["risk_checks"])

    screenshot = meta.get("screenshot")
    for tab, (title, text) in zip(tabs[1:-1], sections, strict=True):
        with tab:
            st.markdown(_for_display(text))
            if title.startswith("Phase 2:") and screenshot and (ROOT_DIR / screenshot).exists():
                st.image(str(ROOT_DIR / screenshot), caption=f"DexScreener chart for {token}, captured with the data")

    with tabs[-1]:
        st.markdown("Download the full report, including the disclaimer, the risk checks and the sources.")
        st.download_button(
            "Download as markdown",
            data=markdown.encode("utf-8"),
            file_name=f"{token}_research_report.md",
            mime="text/markdown",
        )
        pdf, error = markdown_to_pdf(markdown)
        if error:
            st.error(error)
        else:
            st.download_button(
                "Download as PDF", data=pdf, file_name=f"{token}_research_report.pdf", mime="application/pdf"
            )
        if meta.get("cost_usd") is not None:
            st.caption(f"Estimated AI cost of this write-up: ${meta['cost_usd']:.4f} (US Dollars).")


def render():
    token = (st.query_params.get("token") or "").upper()
    if token and report_store.is_valid_token(token):
        _report(token)
    else:
        if token:
            st.error("That link does not point to a valid report. Showing all reports instead.")
        _library()
