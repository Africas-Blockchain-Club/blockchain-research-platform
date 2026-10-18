"""How it works: the method, the risk checks, the AI policy and the legal position."""
import streamlit as st

from config import SETTINGS
from dashboards.ui.components import page_header
from data_analytics.risk_profile import compute_risk_checks


def render():
    page_header(
        "How it works",
        "Research, not advice",
        "What this platform does, what it will never do, and how to check its work.",
    )

    st.subheader("What the platform does")
    st.markdown(
        "It reads public data about a token from the sources listed below, runs rule-based risk "
        "checks on that data, and lays the results out as a report that teaches you how to read "
        "them. The report follows the Blockchain Research Protocol in the `blueprints/` folder: "
        "the project and its news (Phase 0), supply (Phase 1), how the exchange pool sets the "
        "price (Phase 1.5), liquidity (Phase 2), DeFi use (Phase 2.5), leveraged trading "
        "(Phase 3), what the data shows (Phase 4) and long-term factors to watch (Phase 5)."
    )

    st.subheader("What it will never do")
    st.markdown(
        "- Tell you to buy, sell or hold a token.\n"
        "- Give a token a rating, a score, a verdict or a target price.\n"
        "- Tailor anything to your money, goals or circumstances.\n\n"
        "Those things are financial advice. In South Africa, giving financial advice on crypto "
        "assets requires authorisation from the Financial Sector Conduct Authority (FSCA), and "
        f"{SETTINGS.brand_name} is not an authorised provider. Every AI write-up is checked for "
        "advice-style wording before it is saved, and a write-up that fails the check is not published."
    )

    st.subheader("The risk checks")
    st.markdown(
        "Each check compares one number with a teaching threshold. The thresholds are chosen by "
        "this platform to make patterns visible to learners; they are not industry standards. "
        "The checks are never added into a score. **No data** means the platform could not "
        "measure something, which is not the same as the risk being absent."
    )
    rows = "\n".join(
        f"| {c['name']} | {c['threshold']} | {c['source']} |" for c in compute_risk_checks({})
    )
    st.markdown("| Check | Teaching threshold | Source |\n|---|---|---|\n" + rows)

    st.subheader("Data-only reports and AI write-ups")
    st.markdown(
        "A **data-only report** is built by code from the fetched data. It needs no API key and "
        "costs nothing. An **AI write-up** adds plain-English explanation written by an AI model "
        "from the same data. AI can make mistakes, so every write-up names the model that wrote "
        "it, and every number in it should be checked against the sources."
    )
    if not SETTINGS.ai_enabled:
        st.info(f"AI write-ups are switched off on this copy of the platform. {SETTINGS.ai_off_reason}")

    st.subheader("Payments")
    if not SETTINGS.payments_enabled:
        st.markdown("Payments are switched off on this copy of the platform. Every report is free.")
        return
    import payment_verifier

    price = payment_verifier.REPORT_PRICE_USDC
    networks = ", ".join(payment_verifier.NETWORKS[c]["name"] for c in payment_verifier.PAYMENT_CHAINS)
    if payment_verifier.IS_TESTNET:
        st.markdown(
            f"This copy runs the testnet payment demo: an AI write-up is unlocked by a payment of {price} "
            f"test USDC on {networks}. Test USDC has no real-world value. The demo teaches how on-chain "
            "payments work."
        )
    else:
        st.markdown(
            f"Data-only reports are free. An AI write-up costs {price} US Dollars, paid in USDC or USDT on "
            f"any of: {networks}. The payment covers the computing cost of the write-up. It does not buy "
            "advice, and the write-up will never say whether to buy, sell or hold. Blockchain payments cannot "
            "be reversed; if a write-up fails after your payment confirms, you can retry with the same "
            "transaction hash within the hour at no extra cost."
        )
