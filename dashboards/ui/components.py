"""Shared page pieces. Every value that reaches HTML is escaped here."""
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


def offer_card(kicker, title, price, intro, items, note=""):
    """One option on the research page: what it costs and exactly what it contains."""
    rows = "".join(f"<li>{escape(item)}</li>" for item in items)
    note_html = f'<span class="brp-meta">{escape(note)}</span>' if note else ""
    st.html(
        f'<div class="brp-offer"><span class="brp-kicker">{escape(kicker)}</span>'
        f'<div class="brp-offer-head"><h3>{escape(title)}</h3><span class="brp-price">{escape(price)}</span></div>'
        f"<p>{escape(intro)}</p><ul>{rows}</ul>{note_html}</div>"
    )


def footer():
    ai_state = "AI write-ups on" if SETTINGS.ai_enabled else "AI write-ups off"
    if not SETTINGS.payments_enabled:
        pay_state = "payments off"
    else:
        import payment_verifier

        pay_state = "testnet payment demo on" if payment_verifier.IS_TESTNET else "paid AI write-ups on"
    site = escape(SETTINGS.site_url)
    st.html(
        '<footer class="brp-footer">'
        f"<p><strong>{escape(SETTINGS.app_name)}</strong> by {escape(SETTINGS.brand_name)}. "
        f"{escape(SHORT_DISCLAIMER)}</p>"
        "<p>Not an authorised financial services provider. Crypto assets are high risk. "
        "For advice on your own situation, speak to a provider authorised by the FSCA.</p>"
        f'<p>Build {escape(BUILD)} · {ai_state} · {pay_state} · '
        f'<a href="{site}/blockchains/" target="_self">Blockchains</a> · '
        f'<a href="{site}/reports/" target="_self">Reports</a> · '
        f'<a href="{site}/how-it-works.html" target="_self">How it works</a> · '
        f'<a href="{escape(SETTINGS.repo_url)}" target="_blank" rel="noopener">Source code</a></p>'
        "</footer>"
    )
