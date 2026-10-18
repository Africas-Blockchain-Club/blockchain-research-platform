"""
Attack cost (Session 4): price an attack on Ethereum with live data.

The lesson: a proof-of-stake chain is not secure because an attack is
impossible. It is secure because the attack costs more than it can win.
"""
import requests
import streamlit as st

import payment_verifier
from config import SETTINGS
from dashboards.ui.components import notice, page_header


@st.cache_data(ttl=300, show_spinner=False)
def _live_inputs():
    """Live ETH price in USD and the USD to ZAR rate. Returns (eth_usd, usd_zar, sources)."""
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ethereum", "vs_currencies": "usd,zar"},
            timeout=8,
        )
        resp.raise_for_status()
        eth = resp.json().get("ethereum", {})
        if eth.get("usd") and eth.get("zar"):
            return eth["usd"], eth["zar"] / eth["usd"], "CoinGecko (live ETH price in USD and ZAR)"
    except Exception:
        pass
    return None, None, None


def render():
    page_header(
        "Attack cost",
        "What does it cost to attack Ethereum?",
        "A worked example of how proof of stake turns security into a price.",
    )
    st.markdown(
        "Ethereum is secured by validators who each lock up 32 ETH as a deposit (a stake). To halt "
        "the chain or rewrite its history, an attacker must control a large share of all stake, and "
        "the protocol destroys (slashes) stake that is used to cheat. This page prices that attack "
        "with live data."
    )

    eth_usd, usd_zar, source = _live_inputs()
    if eth_usd is None:
        notice(
            "Live price unavailable",
            "The live price feed could not be reached. Set the ETH price by hand from any price site; "
            f"Rand figures use the configured rate of {SETTINGS.fallback_usd_zar} ZAR per USD.",
            tone="warn",
        )
        usd_zar = SETTINGS.fallback_usd_zar

    col_stake, col_price = st.columns(2)
    with col_stake:
        staked_eth = st.number_input(
            "Total ETH staked",
            min_value=1_000_000.0, value=34_000_000.0, step=500_000.0, format="%.0f",
            help="Read the current figure from beaconcha.in before you present. 34 million is a placeholder.",
        )
    with col_price:
        eth_usd = st.number_input(
            "ETH price (US Dollars)", min_value=1.0, value=float(eth_usd or 3000), step=50.0, format="%.0f",
            help="Filled in from the live feed when it is available.",
        )

    attack = st.radio(
        "What is the attacker trying to do?",
        [
            "Stall finality: stop the chain agreeing on its history (needs about 34% of stake)",
            "Control consensus: censor and reorder transactions at will (needs about 51% of stake)",
        ],
    )
    share = 0.34 if attack.startswith("Stall") else 0.51
    eth_needed = staked_eth * share
    cost_usd = eth_needed * eth_usd

    m1, m2, m3 = st.columns(3)
    m1.metric("ETH the attacker must acquire", f"{eth_needed:,.0f} ETH")
    m2.metric("Cost in US Dollars", f"${cost_usd:,.0f}")
    m3.metric("Cost in Rand", f"R{cost_usd * usd_zar:,.0f}")

    reports = cost_usd / float(payment_verifier.REPORT_PRICE_USDC)
    st.markdown(
        f"> **Reading these numbers:** before the attack even starts, the attacker must buy about "
        f"**{eth_needed:,.0f} ETH**, roughly **R{cost_usd * usd_zar:,.0f}**. That is the price of "
        f"about {reports:,.0f} reports at {payment_verifier.REPORT_PRICE_USDC} USDC each."
    )
    st.markdown(
        "> **Why the attack fails anyway:** buying that much ETH pushes its price up, a successful "
        "attack crashes the value of everything the attacker just bought, and the protocol slashes "
        "the stake used to cheat. A blockchain is not secure because an attack is impossible. It is "
        "secure because the attack is a fire that burns the arsonist first."
    )
    st.caption(
        "Simplified on purpose: real attacks also depend on how quickly stake can be bought, on "
        "validator exit queues, and on how the community responds."
        + (f" Live source: {source}, refreshed every 5 minutes." if source else "")
    )
