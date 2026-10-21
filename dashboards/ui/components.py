"""Shared page pieces. Every value that reaches HTML is escaped here."""
from html import escape

import streamlit as st

from config import BUILD, SETTINGS
from data_analytics.chains import FEATURED, PROFILES
from data_analytics.risk_profile import CLEAR, FLAGGED, NO_DATA, STATUS_LABELS
from data_science.compliance import SHORT_DISCLAIMER


def count_search(symbol, page, name=None):
    """Count a search for the Reports page's "What people are researching" list:
    once per coin per visit, since Streamlit reruns the page on every click.
    Only the coin and the time are stored. A database fault never blocks the page."""
    import logging

    import db

    seen = st.session_state.setdefault("counted_searches", set())
    if (page, symbol) in seen:
        return
    seen.add((page, symbol))
    try:
        db.record_search(symbol, page, name)
    except Exception:
        logging.getLogger(__name__).exception("Could not count a search")


def one_line(value):
    """Text that came from a user, made safe to log: a line break in it could
    otherwise forge a second log entry."""
    return str(value).replace("\r", " ").replace("\n", " ")


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


def choose_chain(help_text="The seven blockchains with hand-checked profiles and live network data."):
    """A featured chain from the list, or any chain typed by its full name.
    Returns its ticker when the name is known, otherwise the spelling typed."""
    from tools.report_generator import normalise_token

    featured = [f"{PROFILES[s]['chain']} ({s})" for s in FEATURED]
    # A link (?token=XRP) arrives with its blockchain chosen
    linked = normalise_token(st.query_params.get("token", ""))
    preset = next((i for i, s in enumerate(FEATURED) if s == linked), None)
    col_pick, col_type = st.columns(2)
    with col_pick:
        picked = st.selectbox("Pick a blockchain", featured, index=preset, placeholder="Choose a blockchain",
                              help=help_text)
    with col_type:
        typed = st.text_input("Or type any blockchain's full name", value="" if preset is not None else linked,
                              placeholder="For example Celestia or Cardano",
                              help="Its coin's ticker works too, for example TIA, but the full name is clearer.")
    if picked and not typed.strip():
        return FEATURED[featured.index(picked)]
    raw = " ".join(typed.split())
    # A known name becomes its ticker; anything else keeps the spelling the user typed
    resolved = normalise_token(raw)
    return resolved if resolved != raw.upper() else raw


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
    ai_state = ("write-ups by AI (artificial intelligence) on" if SETTINGS.ai_enabled
                else "write-ups by AI (artificial intelligence) off")
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
        "For advice on your own situation, speak to a provider authorised by the Financial Sector Conduct Authority (FSCA).</p>"
        f'<p>Build {escape(BUILD)} · {ai_state} · {pay_state} · '
        f'<a href="{site}/blockchains/" target="_self">Blockchains</a> · '
        f'<a href="{site}/reports/" target="_self">Reports</a> · '
        f'<a href="{site}/how-it-works.html" target="_self">How it works</a> · '
        f'<a href="{escape(SETTINGS.repo_url)}" target="_blank" rel="noopener">Source code</a></p>'
        "</footer>"
    )
