"""
Attack cost (Session 4): what it takes to attack any blockchain, with live data.

The lesson: a proof-of-stake chain is not secure because an attack is
impossible. It is secure because the attack costs more than it can win, and
that cost falls fast on a smaller chain. Proof of work and trusted validator
lists are explained rather than priced, because buying coins does not attack
them. The models and the maths are in data_analytics/attack_cost.py.
"""
import logging
from html import escape
from urllib.parse import urlsplit

import streamlit as st

from config import SETTINGS
from dashboards.ui.components import choose_chain, count_search, disclaimer_notice, notice, one_line, page_header
from data_analytics import attack_cost as ac
from data_analytics.chains import profile
from data_analytics.formatting import count, usd_zar
from data_engineering.fetchers import fetch_asset_platforms, fetch_coingecko_data, fetch_usd_zar
from data_engineering.staking import fetch_staking
from tools.report_generator import is_valid_query, normalise_token

log = logging.getLogger(__name__)

# Models a user can choose for a chain whose consensus is not known here
CHOOSABLE = ("bft", "longest", "ethereum", "avalanche", "work", "trust")


@st.cache_data(ttl=300, show_spinner=False)
def _market(query):
    token = normalise_token(query)
    return fetch_coingecko_data(token, coin_id=(profile(token) or {}).get("coingecko_id"))


@st.cache_data(ttl=86400, show_spinner=False)
def _platforms():
    return fetch_asset_platforms()


@st.cache_data(ttl=300, show_spinner=False)
def _staking(symbol):
    return fetch_staking(symbol)


@st.cache_data(ttl=3600, show_spinner=False)
def _rand_rate():
    rate, source = fetch_usd_zar()
    return (rate, source) if rate else (SETTINGS.fallback_usd_zar, "configured fallback rate (FALLBACK_USD_ZAR)")


def _share_link(symbol):
    parts = urlsplit(st.context.url or "")
    if parts.scheme in ("http", "https") and parts.netloc:
        return f"{parts.scheme}://{parts.netloc}{parts.path}?token={symbol}"
    return None


def _source_link(url, text="Source"):
    return f'<a class="brp-link" href="{escape(url)}" target="_blank" rel="noopener">{escape(text)}</a>'


def _model_card(model):
    note = f"<p>{escape(model.note)}</p>" if model.note else ""
    st.html(
        f'<div class="brp-notice"><span class="brp-kicker">How {escape(model.label)} reaches agreement</span>'
        f"<p>{escape(model.summary)}</p>{note}<p>{_source_link(model.source, 'Where these figures come from')}</p></div>"
    )
    if model.explainer:
        _explainer_card(model.explainer)


def _explainer_card(explainer):
    """A term taught in full before the figures that depend on it."""
    paragraphs = "".join(f"<p><strong>{escape(lead)}</strong> {escape(text)}</p>" for lead, text in explainer.paragraphs)
    sources = " · ".join(_source_link(url, label) for label, url in explainer.sources)
    st.html(f'<article class="brp-card"><h3>{escape(explainer.title)}</h3>{paragraphs}'
            f'<span class="brp-meta">Sources: {sources}</span></article>')


def _choose_model(symbol, detected):
    known = ac.model_for(symbol)
    if known:
        return known
    labels = [ac.MODELS[k].label for k in CHOOSABLE]
    guess = detected["model"]
    picked = st.selectbox(
        "How does this blockchain reach agreement?", labels,
        index=CHOOSABLE.index(guess) if guess in CHOOSABLE else None, placeholder="Choose its consensus design",
        help="Read it in the blockchain's own documentation, usually under 'consensus'. The share of stake "
             "an attacker needs depends on it.",
    )
    if detected["reason"]:
        suffix = " Change it if the blockchain's documentation says otherwise." if guess else ""
        st.caption(detected["reason"] + suffix)
    return ac.MODELS[CHOOSABLE[labels.index(picked)]] if picked else None


def _explain_work(name):
    st.markdown(
        f"Buying {name} does not attack it. An attacker needs more than half of the computing power that "
        "mines it, for long enough to build a longer chain in secret and then publish it, reversing "
        "payments that looked settled (a double spend)."
    )
    st.markdown(
        "> **Why the size of the chain matters most here:** an attacker does not have to own the mining "
        "power, only rent it. On the largest proof-of-work chains there is not enough rentable power "
        "in the world to do it. On a smaller one there can be. In August 2020 an attacker rented mining "
        "power for Ethereum Classic and reversed payments worth about 807,000 of its coins (ETC), about 5.6 "
        "million US Dollars at the "
        "time, according to Bitquery's investigation, and Ethereum Classic was attacked again within a "
        "week."
    )
    st.html(f"<p>{_source_link(ac.WORK.source, 'Bitquery: the Ethereum Classic attack')}</p>")
    st.caption("This page prices stake, not computing power, so it shows no figure for a proof-of-work chain.")


def _explain_trust(name):
    st.markdown(
        f"{name} has no mining and no staking, so there is nothing to buy. Each server keeps a list of "
        "validators it trusts, and a ledger is accepted when a supermajority of those validators agrees."
    )
    st.markdown(
        "> **What an attack takes instead:** control of enough of the trusted validators, by running them, "
        "bribing their operators or breaking into their servers. The cost is not a price you can read "
        "from a market; it depends on who runs the validators and how independent they are."
    )


def _share_label(share):
    words = {1 / 3: "A third of all stake", 1 / 2: "Half of all stake", 2 / 3: "Two thirds of all stake"}
    return next((w for s, w in words.items() if abs(s - share) < 1e-9), f"{share:.0%} of all stake")


def _attack_cards(results, symbol, rate):
    cards = []
    for attack, r in results:
        coins = f"{r['coins']:,.0f} {symbol}"
        lines = [
            f"<p><strong>{escape(coins)}</strong> to buy and stake</p>",
            f"<p>{escape(usd_zar(r['cost_usd'], rate))}</p>",
        ]
        if r["share_of_unstaked"] is not None:
            if r["share_of_unstaked"] > 1:
                lines.append("<p>More coins than exist outside staking today: there is not enough on the "
                             "market to buy.</p>")
            else:
                lines.append(f"<p>About {r['share_of_unstaked']:.0%} of the coins in circulation that are "
                             "not already staked.</p>")
        if r["days_of_volume"] is not None:
            lines.append(f"<p>About {r['days_of_volume']:,.0f} days of all trading in {escape(symbol)}, "
                         "on every exchange.</p>" if r["days_of_volume"] >= 1 else
                         f"<p>Less than one day of all trading in {escape(symbol)}.</p>")
        cards.append(
            f'<article class="brp-card"><span class="brp-kicker">{escape(_share_label(attack.share))}</span>'
            f"<h3>{escape(attack.goal)}</h3>{''.join(lines)}<p>{escape(attack.what_happens)}</p></article>"
        )
    layout = {1: "one", 3: "fit3"}.get(len(cards), "")
    st.html(f'<div class="brp-grid {layout}">{"".join(cards)}</div>')


def _concentration(staking, symbol):
    stakes = staking["stakes"]
    third = ac.fewest_validators(stakes, 1 / 3)
    two_thirds = ac.fewest_validators(stakes, 2 / 3)
    st.html(
        '<div class="brp-stats" role="list" aria-label="Validator concentration">'
        f'<div class="brp-stat" role="listitem"><span class="v">{len(stakes):,}</span><span class="k">Validators</span></div>'
        f'<div class="brp-stat" role="listitem"><span class="v">{third:,}</span><span class="k">Hold a third</span></div>'
        f'<div class="brp-stat" role="listitem"><span class="v">{two_thirds:,}</span><span class="k">Hold two thirds</span></div>'
        "</div>"
    )
    st.markdown(
        f"> **The shortcut an attacker looks for:** buying stake is the expensive route. The {third:,} largest "
        f"of {len(stakes):,} {symbol} validators together hold a third of all stake. Persuading, bribing or "
        "hacking that many operators reaches the same share without buying a coin, which is why the "
        "number of independent validators matters as much as the price."
    )


def _stake_inputs(symbol, model, market, staking):
    live = staking if staking and "error" not in staking else None
    col_stake, col_price = st.columns(2)
    with col_stake:
        if live:
            hint = f"Live from {live['source']}. Change it to try a different figure."
        elif symbol in ac.STAKE_LOOKUP:
            hint = f"Read the current figure at {ac.STAKE_LOOKUP[symbol]}."
        else:
            hint = "Read it from the blockchain's staking page or a block explorer."
        staked = st.number_input(f"Total {symbol} staked", min_value=0.0, value=live["staked"] if live else None,
                                 step=1_000_000.0, format="%.0f", placeholder="Type the total staked", help=hint)
    with col_price:
        price = st.number_input(f"{symbol} price (US Dollars)", min_value=0.0,
                                value=float(market["price_usd"]) if market.get("price_usd") else None,
                                format="%.4f" if (market.get("price_usd") or 0) < 1 else "%.2f",
                                placeholder="Type the price", help="Live from CoinGecko, refreshed every 5 minutes.")
    if staking and "error" in staking:
        notice("Live staking data unavailable",
               f"The staking source could not be reached ({staking['error']}). Type the total staked instead.",
               tone="warn")
        log.warning("Staking data failed for %s: %s", symbol, staking["error"])
    attacks = model.attacks
    if not attacks:
        share = st.slider("Attacker's share of all stake", 5, 95, 33, format="%d%%",
                          help="There is no single official figure for this chain, so explore the range.") / 100
        attacks = (ac.Attack(share, "Your chosen share", "Explore how the cost grows as the share rises."),)
    return staked, price, attacks, live


def _smaller_chains():
    st.subheader("Why smaller blockchains are easier to attack")
    st.markdown(
        "- **The price falls with the chain.** The same share of stake costs far less when the coin and the "
        "amount staked are small. Try a large chain, then a small one, and compare the cost.\n"
        "- **Fewer validators means fewer people to persuade.** When a handful of operators hold a third of "
        "stake, an attacker can target them instead of the market.\n"
        "- **Thin trading cuts both ways.** Buying a large share of a thinly traded coin pushes its price up "
        "as you buy, but a small market also lets one buyer move it.\n"
        "- **Proof of work can be rented.** Mining power for a small chain can be hired by the hour, which "
        "is how Ethereum Classic was attacked in 2020."
    )


def render():
    page_header(
        "Attack cost",
        "What does it take to attack a blockchain?",
        "Pick any blockchain and see what an attacker would need, priced with live data. It shows why "
        "large blockchains are hard to attack and why smaller ones are easier.",
    )
    disclaimer_notice()

    token = choose_chain(help_text="The seven blockchains with hand-checked profiles.")
    if not token:
        _smaller_chains()
        return
    if not is_valid_query(token):
        st.error("Type the blockchain's full name, for example Celestia or Cardano, using letters, digits "
                 "and spaces only. Check the spelling and try again.")
        return

    with st.spinner("Reading live market data..."):
        market = _market(token)
    if "error" in market:
        log.warning("Attack cost lookup failed for %r: %s", one_line(token), one_line(market["error"]))
        if "not found" in market["error"]:
            st.error(f'No blockchain called "{token}" was found. Check the spelling of its full name, for '
                     "example Celestia, or use its coin's ticker, for example TIA.")
        else:
            st.error(f"Live market data is unavailable just now ({market['error']}). Try again in a minute.")
        return
    symbol, name = market["symbol"], market.get("name") or market["symbol"]
    count_search(symbol, "attack-cost", name)
    st.subheader(f"{name} ({symbol})")

    needs_platforms = market.get("asset_platform_id") and symbol not in ac.CHAIN_MODELS
    detected = ac.detect(market, _platforms() if needs_platforms else {})
    if detected["host"]:
        # A token: the chain it lives on is the one an attacker would have to beat
        notice("Where an attack would happen",
               detected["reason"] + f" Attacking that chain is not the only risk to {name}: a token can also "
               "be hit through its own smart contract, or by whoever controls it (for example, the power to "
               "create more tokens), which this page does not measure.")
        host_market = _market(detected["host"])
        if "error" in host_market:
            st.error(f"Live market data for {detected['host']} is unavailable just now. Try again in a minute.")
            return
        market = host_market
        symbol, name = market["symbol"], market.get("name") or market["symbol"]
        st.subheader(f"What it takes to attack {name} ({symbol})")

    model = _choose_model(symbol, detected)
    if not model:
        notice("Next step", f"Choose how {name} reaches agreement to see what an attack on it would take.")
        _smaller_chains()
        return
    _model_card(model)
    if model.kind == "work":
        _explain_work(name)
        _smaller_chains()
        return
    if model.kind == "trust":
        _explain_trust(name)
        _smaller_chains()
        return

    with st.spinner("Reading live staking data..."):
        staking = _staking(symbol)
    staked, price, attacks, live = _stake_inputs(symbol, model, market, staking)
    if not staked or not price:
        notice("Next step", f"Type the total {symbol} staked and its price to see what each attack would cost.")
        _smaller_chains()
        return

    rate, rate_source = _rand_rate()
    results = [(a, ac.price_attack(staked, a.share, price, market.get("circulating_supply"),
                                   market.get("total_volume_24h_usd"))) for a in attacks]
    _attack_cards(results, symbol, rate)
    st.markdown(
        "> **Why the attacker still loses:** buying that much pushes the price up while you buy, a "
        "successful attack crashes the value of everything you just bought, and on many chains the "
        "protocol destroys (slashes) stake that is used to cheat. A blockchain is not secure because an "
        "attack is impossible. It is secure because the attack is a fire that burns the arsonist first."
    )
    if live:
        _concentration(live, symbol)
    _smaller_chains()

    st.caption(
        f"Simplified on purpose: it assumes the attacker buys new coins at today's price and stakes them, "
        f"which adds to the total ({count(staked)} {symbol} staked now). Real attacks also depend on how "
        "fast stake can be bought and activated, on exit queues, and on how the community responds. "
        f"Prices: CoinGecko. Rand: {rate_source}. Not a safety rating: each chain's figures stand alone."
    )
    link = _share_link(symbol)
    if link:
        st.caption("Share this calculation:")
        st.code(link, language=None)
