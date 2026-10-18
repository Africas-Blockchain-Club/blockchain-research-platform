"""Home: what the platform is, the main actions, and the latest reports."""
from html import escape

import streamlit as st

from config import SETTINGS
from dashboards.ui.components import disclaimer_notice, report_card_html
from tools import report_store


def render():
    # Images come from Streamlit's static server (dashboards/static, served at app/static);
    # the video from SETTINGS.home_video_url. The still is the poster and the fallback,
    # and CSS hides the video for reduced motion.
    video = (
        '<video autoplay muted loop playsinline preload="metadata" poster="app/static/abc-home-still.jpg" '
        f'aria-hidden="true"><source src="{escape(SETTINGS.home_video_url)}" type="video/mp4"></video>'
        if SETTINGS.home_video_url else ""
    )
    st.html(
        '<section class="brp-stage">'
        '<img class="brp-still" src="app/static/abc-home-still.jpg" alt="">'
        f"{video}"
        '<div class="brp-stage-inner"><div class="brp-stage-copy">'
        f'<span class="brp-kicker">{escape(SETTINGS.brand_name)}</span>'
        '<h1 class="brp-display"><span class="line">Learn to</span><span class="line">read a</span>'
        '<span class="line accent">token</span></h1>'
        '<p class="brp-lede">Pull the public data on any crypto token, see which risk checks it trips, and learn '
        "what each number means. This platform teaches research. It does not tell you what to buy or sell.</p>"
        '<div class="brp-actions">'
        '<a class="brp-btn brp-btn-light" href="research" target="_self">Research a token</a>'
        '<a class="brp-btn brp-btn-outline" href="reports" target="_self">Read the reports</a>'
        "</div></div>"
        '<img class="brp-mascot" src="app/static/abc-mascot.png" alt="">'
        "</div></section>"
    )

    st.subheader("How it works")
    st.html(
        '<div class="brp-grid three brp-steps">'
        '<article class="brp-card"><h3>Pick a token</h3><p>Choose a token by its ticker, for example SOL. '
        "The platform reads its public market, supply and exchange data. This step is free.</p></article>"
        '<article class="brp-card"><h3>See the risk checks</h3><p>Ten rule-based checks compare the data '
        "with teaching thresholds. Each one shows the number, the threshold and its source.</p></article>"
        '<article class="brp-card"><h3>Learn what it means</h3><p>Read the full report, phase by phase. '
        "Every table explains how to read it, so you can check the next token on your own.</p></article>"
        "</div>"
    )

    reports = report_store.list_reports(limit=6)
    st.subheader("Latest reports")
    if reports:
        cards = "".join(report_card_html(meta, f"reports?token={meta['token']}") for meta in reports)
        st.html(f'<div class="brp-grid three">{cards}</div>')
    else:
        st.info("No reports yet. Research a token to create the first one.")

    disclaimer_notice()
