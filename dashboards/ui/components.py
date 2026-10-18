"""Shared page pieces. Every value that reaches HTML is escaped here."""
import datetime
from html import escape

import streamlit as st

from config import BUILD, SETTINGS
from data_analytics.risk_profile import CLEAR, FLAGGED, NO_DATA, STATUS_LABELS
from data_science.compliance import SHORT_DISCLAIMER


def page_header(kicker, title, lede=""):
    lede_html = f"<p>{escape(lede)}</p>" if lede else ""
    st.html(
        f'<div class="brp-head"><span class="brp-kicker">{escape(kicker)}</span>'
        f"<h1>{escape(title)}</h1>{lede_html}</div>"
    )


def notice(kicker, text, tone="info"):
    st.html(
        f'<div class="brp-notice {"warn" if tone == "warn" else ""}">'
        f'<span class="brp-kicker">{escape(kicker)}</span><p>{escape(text)}</p></div>'
    )


def disclaimer_notice():
    notice("Education, not advice", SHORT_DISCLAIMER + " Read how this platform works before you rely on anything here.")


def stat_tiles(counts):
    tiles = [(counts[FLAGGED], "Flagged"), (counts[CLEAR], "Clear"), (counts[NO_DATA], "No data")]
    body = "".join(f'<div class="brp-stat"><span class="v">{v}</span><span class="k">{k}</span></div>' for v, k in tiles)
    st.html(f'<div class="brp-stats" role="list" aria-label="Risk check counts">{body}</div>')


def risk_cards(checks):
    cards = []
    for check in checks:
        status = check["status"]
        cards.append(
            f'<article class="brp-card {status}">'
            f'<span class="brp-pill {status}">{STATUS_LABELS[status]}</span>'
            f"<h3>{escape(check['name'])}</h3>"
            f'<p><strong>Measured:</strong> {escape(str(check["value"]))}</p>'
            f'<p><strong>Teaching threshold:</strong> {escape(check["threshold"])}</p>'
            f"<p>{escape(check['measures'])}</p>"
            f"<p>{escape(check['meaning'])}</p>"
            f'<span class="brp-meta">Source: {escape(check["source"])}</span>'
            "</article>"
        )
    st.html(f'<div class="brp-grid three">{"".join(cards)}</div>')


def generated_label(meta):
    try:
        when = datetime.datetime.fromisoformat(meta["generated_at"])
        return when.strftime("%d %b %Y, %H:%M UTC")
    except (KeyError, ValueError):
        return "unknown date"


def mode_pill(meta):
    if meta.get("mode") == "ai":
        return f'<span class="brp-pill ai">AI write-up ({escape(meta.get("model") or "unknown model")})</span>'
    return '<span class="brp-pill">Data only, no AI</span>'


def report_card_html(meta, href):
    return (
        '<article class="brp-card">'
        f"{mode_pill(meta)}"
        f"<h3>{escape(meta.get('name') or meta['token'])} ({escape(meta['token'])})</h3>"
        f'<p>{meta["flagged"]} flagged, {meta["clear"]} clear, {meta["no_data"]} with no data</p>'
        f'<span class="brp-meta">Data from {generated_label(meta)}</span>'
        f'<a class="brp-link" href="{escape(href)}" target="_self">Read the report</a>'
        "</article>"
    )


def footer():
    ai_state = "AI write-ups on" if SETTINGS.ai_enabled else "AI write-ups off"
    if not SETTINGS.payments_enabled:
        pay_state = "payments off"
    else:
        import payment_verifier

        pay_state = "testnet payment demo on" if payment_verifier.IS_TESTNET else f"payments on {payment_verifier.CHAIN_NAME}"
    st.html(
        '<footer class="brp-footer">'
        f"<p><strong>{escape(SETTINGS.app_name)}</strong> by {escape(SETTINGS.brand_name)}. "
        f"{escape(SHORT_DISCLAIMER)}</p>"
        "<p>Not an authorised financial services provider. Crypto assets are high risk. "
        "For advice on your own situation, speak to a provider authorised by the FSCA.</p>"
        f'<p>Build {escape(BUILD)} · {ai_state} · {pay_state} · '
        f'<a href="{escape(SETTINGS.repo_url)}" target="_blank" rel="noopener">Source code</a></p>'
        "</footer>"
    )
