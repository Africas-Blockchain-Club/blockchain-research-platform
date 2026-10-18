"""
Research a token: fetch the data (free), see the risk checks, then save a
data-only report or an AI write-up.

The AI write-up sits behind the testnet payment demo only when
PAYMENTS_ENABLED is true. Nothing after the payment gate costs anything
until a transaction verifies on-chain.
"""
import re
import uuid

import requests
import streamlit as st
from sqlalchemy.exc import IntegrityError

import db
import emailer
import payment_verifier
from config import SETTINGS
from dashboards.ui.components import disclaimer_notice, notice, page_header, risk_cards, stat_tiles
from dashboards.ui.wallet import wallet_connect, wallet_pay
from data_analytics.risk_profile import summarise_checks
from data_science.compliance import AdviceLanguageError
from data_science.llm import AIRefusalError, AIResponseError, AIUnavailableError
from payment_verifier import PaymentVerificationError
from tools import report_store
from tools.report_generator import fetch_and_analyse, normalise_token, save_ai_report, save_data_report

STABLECOINS = {"USDT", "USDC", "BUSD", "DAI", "TUSD", "USDD", "FRAX", "USDP", "GUSD",
               "LUSD", "SUSD", "CUSD", "FDUSD", "PYUSD", "USDE", "EURC", "USDS"}
FALLBACK_TOP_TOKENS = ["BTC", "ETH", "SOL", "BNB", "AVAX", "DOT", "LINK", "ADA", "ARB", "OP"]
AI_ERRORS = (AIUnavailableError, AIRefusalError, AIResponseError, AdviceLanguageError)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@st.cache_data(ttl=604800, show_spinner=False)  # the list changes slowly; refresh weekly
def top_tokens():
    """The ten largest non-stablecoin tokens by market cap, or a fixed list
    when CoinGecko cannot be reached. Returns (symbols, note)."""
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1},
            timeout=10,
        )
        resp.raise_for_status()
        symbols = []
        for coin in resp.json():
            symbol = coin.get("symbol", "").upper()
            if symbol and symbol not in STABLECOINS and symbol not in symbols:
                symbols.append(symbol)
            if len(symbols) == 10:
                break
        return symbols, "Ten largest by market cap, from CoinGecko"
    except Exception:
        return FALLBACK_TOP_TOKENS, "CoinGecko was unavailable, so this is a fixed list"


def _choose_token():
    symbols, note = top_tokens()
    col_pick, col_type = st.columns(2)
    with col_pick:
        picked = st.selectbox("Pick a token", symbols, index=None, placeholder="Choose a token", help=note)
    with col_type:
        typed = st.text_input("Or type a ticker or name", placeholder="For example ENA or solana")
    raw = typed.strip() or (picked or "")
    return normalise_token(raw) if raw else ""


def _fetch(token):
    with st.status(f"Fetching public data for {token}...", expanded=True) as status:
        try:
            analysis = fetch_and_analyse(token, log_fn=status.write)
        except Exception as e:
            status.update(label=f"Could not fetch data for {token}", state="error", expanded=True)
            st.error(f"{e}")
            return
        status.update(label=f"Data for {token} is ready", state="complete", expanded=False)
    st.session_state["analysis"] = analysis
    st.session_state["analysis_id"] = str(uuid.uuid4())


def _saved(meta):
    st.success(f"The {meta['token']} report is saved.")
    st.html(f'<a class="brp-link" href="reports?token={meta["token"]}" target="_self">Read the {meta["token"]} report</a>')


def _write_ai(analysis, model, payment_id=None):
    with st.spinner(f"Writing the report with {model}. This can take a few minutes..."):
        try:
            return save_ai_report(analysis, model=model, payment_id=payment_id)
        except AI_ERRORS as e:
            st.error(f"{e}")
            st.caption("Nothing was saved. You can still save the data-only report.")
            return None


def _email_receipt(email, meta, verified, tx_hash):
    saved = db.get_latest_report(meta["token"])
    try:
        emailer.send_report_receipt(
            payer_email=email,
            token=meta["token"],
            report_markdown=saved["markdown"],
            receipt={
                "amount_decimal": verified["amount_decimal"],
                "asset": verified["asset_symbol"],
                "chain_id": verified["chain_id"],
                "chain_name": verified["chain_name"],
                "tx_hash": tx_hash,
                "testnet": payment_verifier.IS_TESTNET,
                "flagged": meta["flagged"],
                "clear": meta["clear"],
                "no_data": meta["no_data"],
            },
        )
        st.success(f"The report and receipt were emailed to {email}.")
    except (emailer.EmailNotConfiguredError, emailer.EmailDeliveryError) as e:
        st.warning(
            f"Your report is saved and shown below, but the email to {email} could not be sent. "
            "The operator has been told and will send it."
        )
        emailer.alert_owner(
            f"Write-up email to a payer failed ({meta['token']})",
            f"A paid write-up was saved but could not be emailed.\n\nPayer email: {email}\n"
            f"Token: {meta['token']}\nTransaction: {_tx_link(verified, tx_hash)}\nError: {e}\n\n"
            "Send the report by hand from the Reports page (Download tab).",
        )


def _tx_link(verified, tx_hash):
    return f"{payment_verifier.NETWORKS[verified['chain_id']]['explorer']}/tx/{tx_hash}"


def _verify_payment(analysis, tx_hash, chain_id, email):
    """Verify on-chain and record the payment. Returns the verified payment
    dict with its database id under "payment_id", or None."""
    try:
        with st.spinner("Checking the payment on-chain..."):
            verified = payment_verifier.wait_for_payment(tx_hash, chain_id)
        payment_id = db.record_payment_attempt(
            request_id=st.session_state["analysis_id"],
            token_symbol=analysis["token"],
            payer_address=verified["payer_address"],
            recipient_address=payment_verifier.RECIPIENT_ADDRESS,
            chain_id=verified["chain_id"],
            asset_contract=verified["asset_contract"],
            asset_symbol=verified["asset_symbol"],
            amount_atomic=verified["amount_atomic"],
            amount_decimal=verified["amount_decimal"],
            tx_hash=tx_hash,
            payer_email=email or None,
            verification_method=verified["verification_method"],
        )
        db.mark_payment_confirmed(payment_id, verified["confirmations"])
        emailer.alert_owner(
            f"Payment received: {verified['amount_decimal']} {verified['asset_symbol']} for {analysis['token']}",
            f"A payment unlocked an AI write-up.\n\n"
            f"Token researched: {analysis['token']}\n"
            f"Amount: {verified['amount_decimal']} {verified['asset_symbol']} on {verified['chain_name']}\n"
            f"Payer: {verified['payer_address']}\n"
            f"Transaction: {_tx_link(verified, tx_hash)}\n\n"
            "Check your Anthropic credit balance and top it up if it is running low:\n"
            "https://console.anthropic.com/settings/billing\n",
        )
        return dict(verified, payment_id=payment_id)
    except PaymentVerificationError as e:
        st.error(f"The payment could not be verified: {e}")
    except IntegrityError:
        # Already recorded. If its write-up never arrived (a failure, or the page
        # was closed), the payer may use the same transaction again for that token.
        existing = db.get_payment_by_tx_hash(tx_hash)
        if (existing and existing["status"] == "confirmed" and existing["token_symbol"] == analysis["token"]
                and not db.report_exists_for_payment(existing["id"])):
            st.info("This payment was already confirmed, and its write-up was never delivered. Writing it now.")
            return {
                "payment_id": existing["id"],
                "amount_decimal": existing["amount_decimal"],
                "asset_symbol": existing["asset_symbol"],
                "chain_id": existing["chain_id"],
                "chain_name": payment_verifier.NETWORKS[existing["chain_id"]]["name"],
                "payer_address": existing["payer_address"],
            }
        st.error(
            "This transaction has already been used to unlock a report. If it was for a different token, "
            "research that token to use it."
        )
    return None


def _write_paid(analysis, model, payment, tx_hash, email):
    """Write the AI report for a confirmed payment, telling the owner if it fails."""
    meta = _write_ai(analysis, model, payment_id=payment["payment_id"])
    if meta is None:
        emailer.alert_owner(
            f"Paid write-up failed for {analysis['token']}",
            f"A payer was charged but the AI write-up failed. They can retry with the same transaction "
            f"within {payment_verifier.MAX_PAYMENT_AGE_MINUTES} minutes; check the logs if it keeps failing.\n\n"
            f"Token: {analysis['token']}\nModel: {model}\n"
            f"Payment: {payment['amount_decimal']} {payment['asset_symbol']} on {payment['chain_name']}\n"
            f"Transaction: {_tx_link(payment, tx_hash)}\n"
            "Logs: fly logs --app blockchain-research-platform\n",
        )
        return
    if email:
        _email_receipt(email, meta, payment, tx_hash)
    st.session_state.setdefault("paid", {}).pop(analysis["token"], None)
    _saved(meta)


def _payment_gate(analysis, model):
    """Take a payment in any accepted stablecoin, then write the report."""
    token = analysis["token"]
    if not payment_verifier.RECIPIENT_ADDRESS:
        st.error("Payments are switched on but REPORT_RECIPIENT_ADDRESS is not set.")
        return

    paid = st.session_state.setdefault("paid", {})
    if token in paid:
        # Paid already: a failed write-up can be retried without paying twice
        st.info("Your payment for this token is confirmed.")
        if st.button("Try the AI write-up again", type="primary"):
            entry = paid[token]
            _write_paid(analysis, model, entry["payment"], entry["tx_hash"], entry["email"])
        return

    price = payment_verifier.REPORT_PRICE_USDC
    networks = ", ".join(payment_verifier.NETWORKS[c]["name"] for c in payment_verifier.PAYMENT_CHAINS)
    if payment_verifier.IS_TESTNET:
        st.markdown(
            f"Pay **{price} test USDC** on {networks} to unlock the AI write-up. Test USDC has no real-world "
            "value: this is a demonstration of on-chain payments, and the payment covers the computing cost "
            "of the write-up, not advice."
        )
    else:
        st.markdown(
            f"Pay **{price} US Dollars in USDC or USDT** to unlock the AI write-up for {token}. Use whichever "
            f"you already hold, on any of: {networks}. Your wallet shows what you can pay with."
        )
        notice(
            "What you are paying for",
            "An AI-written explanation of the public data shown above, checked for advice language before it "
            "is saved. You are paying for the computing cost of that write-up, not for advice: it will not "
            "say whether to buy, sell or hold. If the write-up fails after your payment confirms, paste the "
            "same transaction hash below within the hour to try again at no extra cost. Payments on a "
            "blockchain cannot be reversed, so check the token before you pay.",
            tone="warn",
        )
    # Every paid write-up is emailed to the payer, so a payment is only taken
    # when email works and the payer has given an address.
    if not emailer.is_configured():
        st.error("Email delivery is not set up, so payments are paused. Please try again later.")
        return
    email = st.text_input(
        "Your email address",
        placeholder="you@example.com",
        help="The write-up and your receipt are emailed here as soon as the payment confirms.",
    ).strip()
    if not EMAIL_PATTERN.match(email):
        st.info("Enter your email address to continue. Your write-up and receipt are sent there.")
        return

    result = wallet_pay(
        price=str(price),
        recipient=payment_verifier.RECIPIENT_ADDRESS,
        asset_label=payment_verifier.ASSET_LABEL,
        options=payment_verifier.payment_options(),
        key=f"wallet_pay_{token}",
        default=None,
    )

    tx_hash, chain_id = None, None
    # The component re-sends its last value on every rerun; handle each hash once
    handled = st.session_state.setdefault("handled_tx", set())
    if result and result.get("tx_hash") and result["tx_hash"] not in handled:
        tx_hash, chain_id = result["tx_hash"].strip(), int(result["chain_id"])
        handled.add(tx_hash)

    with st.expander("No wallet extension, or retrying a paid write-up? Paste the transaction hash"):
        chain_names = {payment_verifier.NETWORKS[c]["name"]: c for c in payment_verifier.PAYMENT_CHAINS}
        typed_chain = st.selectbox("Network you paid on", list(chain_names))
        st.caption(
            f"Send {price} USDC or USDT on {typed_chain} to {payment_verifier.RECIPIENT_ADDRESS}, then paste "
            f"the transaction hash within {payment_verifier.MAX_PAYMENT_AGE_MINUTES} minutes."
        )
        typed_hash = st.text_input("Transaction hash", placeholder="0x...")
        if st.button("Check the payment"):
            tx_hash, chain_id = typed_hash.strip(), chain_names[typed_chain]

    if tx_hash:
        payment = _verify_payment(analysis, tx_hash, chain_id, email)
        if payment:
            paid[token] = {"payment": payment, "tx_hash": tx_hash, "email": email}
            _write_paid(analysis, model, payment, tx_hash, email)


def _wallet_identity():
    with st.expander("Sign in with your wallet (optional)"):
        st.caption("Your wallet address is an identity you own outright. Unlike an email account, nobody can suspend it.")
        identity = wallet_connect(key="wallet_identity_component", default=None)
        if identity and identity.get("address"):
            st.session_state["wallet_identity"] = identity["address"]
        address = st.session_state.get("wallet_identity")
        if address:
            st.success(f"Signed in as {address[:6]}...{address[-4:]}")
            past = db.get_payments_by_payer(address)
            st.caption(f"Reports unlocked by this wallet: {len(past)}")


def render():
    page_header(
        "Step 1: free data",
        "Research a token",
        "Fetch the public data first. It is free, and it shows the risk checks straight away.",
    )
    disclaimer_notice()

    token = _choose_token()
    fetch = st.button("Fetch the data" if token else "Choose a token first", type="primary", disabled=not token)
    if fetch:
        if not report_store.is_valid_token(token):
            st.error("Tickers use letters and digits only, for example SOL. Check the spelling and try again.")
        else:
            _fetch(token)

    analysis = st.session_state.get("analysis")
    if not analysis:
        return

    st.divider()
    st.subheader(f"Risk checks for {analysis['token']}")
    stat_tiles(summarise_checks(analysis["risk_checks"]))
    risk_cards(analysis["risk_checks"])

    st.subheader("Save the report")
    col_data, col_ai = st.columns(2, border=True)
    with col_data:
        st.markdown("**Data-only report**")
        st.caption("Built by code from the data above. Free, and no AI is involved.")
        if st.button("Save the data-only report", use_container_width=True):
            _saved(save_data_report(analysis))
    with col_ai:
        st.markdown("**AI write-up**")
        st.caption("Adds plain-English explanation written by an AI model, checked for advice language before it is saved.")
        if not SETTINGS.ai_enabled:
            notice("AI is off", SETTINGS.ai_off_reason, tone="warn")
            return
        if SETTINGS.ai_requires_payment and not SETTINGS.payments_enabled:
            notice("Not available yet", "AI write-ups on this site need a payment, and payments are not switched on yet.", tone="warn")
            return
        model = st.selectbox("AI model", SETTINGS.ai_models, help="The first model in AI_MODELS is the default.")
        if SETTINGS.payments_enabled:
            _wallet_identity()
            _payment_gate(analysis, model)
        elif st.button("Write the AI report", type="primary", use_container_width=True):
            meta = _write_ai(analysis, model)
            if meta:
                _saved(meta)
