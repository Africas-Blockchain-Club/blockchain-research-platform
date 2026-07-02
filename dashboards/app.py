import streamlit as st
import os
import sys
import re
import uuid
import datetime
import markdown
import html
from xhtml2pdf import pisa
from io import BytesIO
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

load_dotenv()

# Import the report generator
# (triggering hot reload)
import importlib
# Add the project root to sys.path so subagents (data_engineering, etc.) can be found
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

sys.path.append(os.path.join(root_path, 'tools'))
import report_generator
importlib.reload(report_generator)
from report_generator import (
    generate_report,
    fetch_and_analyse,
    generate_ai_and_save,
    extract_blueprint_score,
    extract_final_verdict,
    normalise_token,
)
from data_science.ai_generator import infer_verdict_from_score

import db
import payment_verifier
from payment_verifier import PaymentVerificationError

import data_science.anthropic_analyst as _analyst_mod
importlib.reload(_analyst_mod)
from data_science.anthropic_analyst import generate_anthropic_brief, HAIKU, SONNET, OPUS

st.set_page_config(page_title="ABC Research Dashboard", layout="wide")

# Professional large title
st.markdown("""
<h1 style='font-size: 3em; text-align: center; margin-bottom: 0.5em;'>
Africa's Blockchain Club Research Dashboard
</h1>
""", unsafe_allow_html=True)

st.caption("Forensic token research covering supply, liquidity, macro environment, derivatives, and regulatory risk. Structured for investment decisions, built for learning.")

# Sidebar - two nav items only; reports are opened from the Overview card grid
st.sidebar.header("Navigation")

blueprints_dir = os.path.join(root_path, "blueprints")
reports_dir = os.path.join(root_path, "reports")

if not os.path.exists(blueprints_dir): os.makedirs(blueprints_dir)
if not os.path.exists(reports_dir): os.makedirs(reports_dir)

db.init_db()

blueprint_files = [f for f in os.listdir(blueprints_dir) if f.endswith(".md")]

import glob
_raw_report_paths = glob.glob(os.path.join(reports_dir, "*_audit_report.md"))
# Newest first, cap at 10 for the dashboard — older files stay on disk
_raw_report_paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
report_files = [os.path.relpath(p, reports_dir) for p in _raw_report_paths[:10]]

display_reports = []
for rep in report_files:
    token_name = os.path.basename(rep).split('_')[0].upper()
    display_reports.append(f"Report: {token_name}")

# Sidebar only shows primary nav; reports open via card clicks
SIDEBAR_PAGES = ["Overview", "Generate Report"]
all_pages = SIDEBAR_PAGES + display_reports

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Overview"
if st.session_state.selected_page not in all_pages:
    st.session_state.selected_page = "Overview"

def update_page():
    st.session_state.selected_page = st.session_state.sidebar_radio

# When viewing a report page, keep sidebar selection on Overview
sidebar_index = (
    SIDEBAR_PAGES.index(st.session_state.selected_page)
    if st.session_state.selected_page in SIDEBAR_PAGES
    else 0
)

st.sidebar.radio(
    "Go to",
    SIDEBAR_PAGES,
    index=sidebar_index,
    key="sidebar_radio",
    on_change=update_page,
)

# Sidebar: show report shortcuts as plain links when reports exist
if display_reports:
    st.sidebar.markdown("---")
    st.sidebar.caption("Reports")
    for label in display_reports:
        token = label.split(": ")[1]
        if st.sidebar.button(label, key=f"sb_{token}", use_container_width=True):
            st.session_state.selected_page = label
            st.rerun()

page = st.session_state.selected_page


# ====================== PDF GENERATOR ======================
def clean_markdown_for_pdf(md_text):
    md_text = md_text.replace('■', '-')
    md_text = md_text.replace('•', '-')
    md_text = md_text.replace('—', '&mdash;')
    md_text = md_text.replace('–', '&ndash;')
    md_text = md_text.replace(' / ', '&nbsp;/&nbsp;')
    md_text = md_text.replace('\u201c', '"').replace('\u201d', '"')
    md_text = md_text.replace('\u2018', "'").replace('\u2019', "'")
    return md_text


def md_to_pdf(md_text, filename):
    md_text = clean_markdown_for_pdf(md_text)
    html_content = markdown.markdown(md_text, extensions=['extra', 'tables'])
    html_content = html.unescape(html_content)
    html_content = html_content.replace('±', '&plusmn;')
    html_content = html_content.replace('→', '&rarr;')
    html_content = html_content.replace('—', '&mdash;')
    html_content = html_content.replace('–', '&ndash;')

    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: a4; margin: 1.5cm 1.5cm; }}
            body {{ font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.4; color: rgb(33, 33, 33); }}
            h1 {{ font-size: 16pt; font-weight: bold; margin-top: 0; margin-bottom: 12pt; color: rgb(0,0,0); border-bottom: 2pt solid rgb(200,200,200); padding-bottom: 4pt; }}
            h2 {{ font-size: 13pt; font-weight: bold; margin-top: 14pt; margin-bottom: 8pt; color: rgb(51,51,51); }}
            h3 {{ font-size: 11pt; font-weight: bold; margin-top: 10pt; margin-bottom: 6pt; color: rgb(68,68,68); }}
            p {{ margin-bottom: 6pt; text-align: justify; }}
            ul, ol {{ margin-left: 12pt; margin-bottom: 8pt; padding-left: 8pt; }}
            li {{ margin-bottom: 4pt; line-height: 1.4; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10pt 0; font-size: 8.5pt; table-layout: auto; }}
            td, th {{ border: 0.5pt solid rgb(180,180,180); padding: 5pt 3pt; text-align: left; vertical-align: top; }}
            th {{ background-color: rgb(240,240,240); font-weight: bold; text-align: center; }}
            tr:nth-child(even) {{ background-color: rgb(250,250,250); }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(styled_html, dest=pdf_buffer)
    if pisa_status.err:
        st.error(f"PDF generation error: {pisa_status.err}")
    st.download_button(
        label=f"📄 Download {filename}",
        data=pdf_buffer.getvalue(),
        file_name=filename,
        mime="application/pdf"
    )


def load_md(path):
    full_path = os.path.join(os.getcwd(), path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    
    # Fallback to absolute if it was passed absolutely
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
            
    return "## File not found – check path"


def extract_score_colour(score):
    """Return colour and label based on Blueprint Score"""
    if score >= 60:
        return "🟢", "normal"
    elif score >= 30:
        return "🟡", "off"
    else:
        return "🔴", "inverse"


def extract_verdict_emoji(verdict):
    """Return emoji for verdict rating"""
    mapping = {
        "Strong Buy": "🟢",
        "Accumulate": "🟢",
        "Neutral": "🟡",
        "Distribute": "🔴",
        "Strong Sell": "🔴",
    }
    return mapping.get(verdict, "⚪")

def extract_metadata_frontmatter(md_text):
    """Extract YAML-style frontmatter generated by the orchestrator."""
    metadata = {}
    content = md_text
    match = re.search(r'^---\n(.*?)\n---\n(.*)', md_text, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        content = match.group(2)
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip()] = val.strip()
    return metadata, content


def split_report_phases(md_text):
    """Split report markdown into phase sections for tabbed display"""
    sections = {}
    current_key = "Overview"
    current_lines = []

    for line in md_text.split("\n"):
        # Detect any standard '## ' H2 header as a new tab boundary
        if line.startswith("## "):
            # Save the previous section
            if current_lines:
                sections[current_key] = "\n".join(current_lines)
            
            # Clean up the new header text to use as the Tab Name
            raw_title = line.replace("## ", "").strip()
            # If it's too long, truncate it
            if len(raw_title) > 30:
                raw_title = raw_title[:27] + "..."
                
            current_key = raw_title
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_key] = "\n".join(current_lines)

    return sections


_TABLE_CENTRE_CSS = """
<style>
/* Centre all markdown tables in report sections */
[data-testid="stMarkdownContainer"] table {
    margin-left: auto;
    margin-right: auto;
    width: 100%;
}
</style>
"""


def clean_report_for_display(text):
    """
    Preprocess report markdown before passing to st.markdown.
    - Injects CSS to centre tables.
    - Escapes $ signs so Streamlit does not treat them as LaTeX math delimiters.
    - Replaces any em/en dashes that slipped through AI generation.
    """
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace('$', r'\$')
    return _TABLE_CENTRE_CSS + text


# ====================== TOP TOKENS (auto-refreshes weekly) ======================

STABLECOINS = {"USDT", "USDC", "BUSD", "DAI", "TUSD", "USDD", "FRAX", "USDP", "GUSD",
               "LUSD", "SUSD", "CUSD", "FDUSD", "PYUSD", "USDE", "EURC"}

FALLBACK_TOP_TOKENS = ["BTC", "ETH", "SOL", "BNB", "AVAX", "DOT", "LINK", "ADA", "ARB", "OP"]


@st.cache_data(ttl=604800, show_spinner=False)  # refresh once a week
def fetch_top_tokens():
    """
    Fetch the top utility tokens from CoinGecko by market cap, excluding stablecoins.
    BTC is always index 0, ETH always index 1.
    Returns (list_of_symbols, fetched_at_str).
    """
    import datetime as dt
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets"
            "?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
            "&sparkline=false",
            timeout=10,
        )
        if resp.status_code != 200:
            return FALLBACK_TOP_TOKENS, "fallback (API unavailable)"

        coins = resp.json()
        seen = {"BTC", "ETH"}
        top = ["BTC", "ETH"]
        for coin in coins:
            sym = coin.get("symbol", "").upper()
            if sym in seen or sym in STABLECOINS:
                continue
            top.append(sym)
            seen.add(sym)
            if len(top) == 10:
                break

        fetched_at = dt.datetime.utcnow().strftime("%d %b %Y")
        return top, fetched_at
    except Exception:
        return FALLBACK_TOP_TOKENS, None


# ====================== MAIN LOGIC ======================
if page == "Overview":
    st.markdown("""
    <style>
    .dashboard-container {
        padding: 1rem 0;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 1.5rem;
        margin-top: 2rem;
        border-bottom: 2px solid var(--secondary-background-color);
        padding-bottom: 0.5rem;
    }
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 1.5rem;
    }
    .inst-card {
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-top: 4px solid #0284c7;  /* Primary blue for Blueprints */
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .inst-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
    }
    .inst-card.report-card {
        border-top: 4px solid #10b981;  /* Emerald for Reports */
    }
    .card-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 0.75rem;
    }
    .card-meta {
        font-size: 0.9rem;
        color: var(--text-color);
        opacity: 0.8;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }
    .meta-tag {
        display: inline-block;
        background: rgba(128, 128, 128, 0.15);
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
        color: var(--text-color);
        opacity: 0.9;
    }
    .score-badge {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-color);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    
    # --- BLUEPRINTS SECTION ---
    # The user specifically requested to hide the framework IP (Blueprints)
    # so we will no longer render blueprint cards on the public-facing dashboard.
    
    # --- LATEST REPORTS SECTION ---
    st.markdown('<div class="section-title">Investment Intelligence Reports (Live Feed)</div>', unsafe_allow_html=True)
    
    # Create rows of 3 columns to hold the report cards
    cols = st.columns(3)
    
    for i, rep in enumerate(report_files):
        token_name = os.path.basename(rep).split('_')[0].upper()

        rep_path = os.path.join(reports_dir, rep)
        score = 0
        verdict = "Unknown"
        if os.path.exists(rep_path):
            raw_md = load_md(rep_path)
            meta, md = extract_metadata_frontmatter(raw_md)
            score = meta.get("Score", extract_blueprint_score(md))
            verdict = meta.get("Verdict", extract_final_verdict(md))
            if verdict == "Unknown" and int(score) > 0:
                verdict = infer_verdict_from_score(int(score))

        emoji = extract_verdict_emoji(verdict)

        # Staleness calculation
        age_days = 0
        if os.path.exists(rep_path):
            mtime = os.path.getmtime(rep_path)
            age_days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime)).days

        is_stale = age_days >= 7
        if age_days < 3:
            fresh_color = "#10b981"
            fresh_label = f"{age_days}d ago" if age_days > 0 else "Today"
        elif age_days < 7:
            fresh_color = "#f59e0b"
            fresh_label = f"{age_days}d ago"
        else:
            fresh_color = "#ef4444"
            fresh_label = f"{age_days}d ago"

        card_html = f"""
<div class="inst-card report-card" style="margin-bottom: 0.5rem; height: 100%;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <div class="meta-tag" style="background: rgba(16, 185, 129, 0.2); color: #10b981; margin-bottom: 0;">Data Extraction: Live & Autonomous</div>
        <span style="font-size: 0.72rem; font-weight: 700; color: {fresh_color}; background: rgba(128,128,128,0.1); padding: 0.2rem 0.5rem; border-radius: 4px; white-space: nowrap;">{fresh_label}</span>
    </div>
    <div class="card-title">{token_name} Insight Report</div>
    <div class="card-meta">
        <strong>Contents:</strong> Unbiased forensic audit to support profitable investment decisions. Features live data snapshots, derivatives checks, and generative Alpha assessment.<br><br>
        <strong>Framework:</strong> Derived from ABC Premium Analysis Blueprints.
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 1rem; border-top: 1px solid rgba(128, 128, 128, 0.2);">
        <div>
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-color); font-weight: 600; opacity: 0.8;">Blueprint Score</span><br>
            <span class="score-badge">{score}/100</span>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-color); font-weight: 600; opacity: 0.8;">Verdict</span><br>
            <span style="font-weight: 700; color: var(--text-color); font-size: 1.1rem;">{emoji} {verdict}</span>
        </div>
    </div>
</div>
"""
        with cols[i % 3]:
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"View {token_name} Report", key=f"btn_{token_name}"):
                st.session_state.selected_page = f"Report: {token_name}"
                st.rerun()
            if is_stale:
                if st.button(f"Regenerate {token_name}", key=f"regen_{token_name}", type="primary", use_container_width=True):
                    st.session_state.regen_token = token_name
                    st.session_state.selected_page = "Generate Report"
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Generate Report":
    st.header("Generate New Forensic Audit")
    st.info(
        "Each report runs five forensic phases: narrative and macro context (Phase 0), "
        "supply forensics (Phase 1), market structure and liquidity (Phase 2), "
        "derivatives and sentiment (Phase 3), and a Blueprint Score with SWOT analysis and Final Verdict (Phase 4). "
        "A Kill Switch checklist flags thin liquidity, unlock cliffs, whale dominance, and wash trading. "
        "Every section includes an ABC (Africa's Blockchain Club) callout explaining what the numbers mean "
        "and why they matter - written for both analysts and blockchain developer prospects reading the research for the first time."
    )

    top_tokens, list_updated = fetch_top_tokens()

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        token_label = f"Top 10 by utility (updated {list_updated})" if list_updated else "Top 10 by utility"
        tokens = st.multiselect(
            token_label,
            options=top_tokens,
            default=[],
            placeholder="Select one or more tokens...",
        )
    with col2:
        if "regen_token" in st.session_state:
            st.session_state["custom_token_input"] = st.session_state.pop("regen_token")
        custom_token = st.text_input("Other token", placeholder="e.g., ENA, MATIC", key="custom_token_input")
    with col3:
        model_choice = st.selectbox(
            "Model",
            ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-8"],
            help="Haiku is fastest. Sonnet is thorough. Opus goes deepest."
        )

    date = st.date_input("Report Date", datetime.date.today())

    # Normalise so "solana" -> "SOL", "ethereum" -> "ETH" etc. before generating
    all_tokens = list({normalise_token(t) for t in tokens})
    if custom_token.strip():
        all_tokens.append(normalise_token(custom_token.strip()))

    if st.button("Fetch Data", type="primary"):
        if not all_tokens:
            st.warning("Please select or enter at least one token.")
        else:
            st.session_state.setdefault("pending_payments", {})
            for token in all_tokens:
                with st.status(f"Fetching {token.upper()} data...", expanded=True) as status:
                    try:
                        result = fetch_and_analyse(token, log_fn=status.write)
                        st.session_state.pending_payments[token] = {
                            "data_summary": result["data_summary"],
                            "kill_switches": result["kill_switches"],
                            "screenshot_path": result["screenshot_path"],
                            "model": model_choice,
                            "request_id": str(uuid.uuid4()),
                        }
                        status.update(
                            label=f"{token.upper()} data ready — pay to unlock the AI report.",
                            state="complete",
                            expanded=False,
                        )
                    except Exception as e:
                        status.update(
                            label=f"{token.upper()} failed: {str(e)[:80]}",
                            state="error",
                            expanded=True,
                        )

    # Payment gate - shown once data has been fetched for a token but the AI report
    # (the paid stage) hasn't run yet. Nothing below this point costs anything until
    # a transaction hash verifies on-chain.
    if st.session_state.get("pending_payments"):
        st.divider()
        st.subheader("Pay to Unlock")
        st.caption(
            f"Each report costs {payment_verifier.REPORT_PRICE_USDC} USDC on Base Sepolia "
            f"(chain {payment_verifier.CHAIN_ID}). Send it to `{payment_verifier.RECIPIENT_ADDRESS}`, "
            f"then paste the transaction hash below."
        )
        for token in list(st.session_state.pending_payments.keys()):
            pending = st.session_state.pending_payments[token]
            with st.container(border=True):
                st.markdown(f"**{token}** — awaiting payment")
                tx_hash = st.text_input("Transaction hash", key=f"tx_hash_{token}", placeholder="0x...")
                if st.button(f"Verify Payment & Generate ({token})", key=f"verify_{token}"):
                    try:
                        with st.spinner("Verifying payment on-chain..."):
                            verified = payment_verifier.verify_payment(tx_hash.strip())

                        payment_id = db.record_payment_attempt(
                            request_id=pending["request_id"],
                            token_symbol=token,
                            payer_address=verified["payer_address"],
                            recipient_address=payment_verifier.RECIPIENT_ADDRESS,
                            chain_id=payment_verifier.CHAIN_ID,
                            asset_contract=payment_verifier.USDC_CONTRACT,
                            asset_symbol="USDC",
                            amount_atomic=verified["amount_atomic"],
                            amount_decimal=verified["amount_decimal"],
                            tx_hash=tx_hash.strip(),
                            verification_method=verified["verification_method"],
                        )
                        db.mark_payment_confirmed(payment_id, verified["confirmations"])

                        with st.spinner(f"Generating {token} report..."):
                            generate_ai_and_save(
                                token,
                                pending["data_summary"],
                                pending["kill_switches"],
                                pending["screenshot_path"],
                                model=pending["model"],
                                payment_id=payment_id,
                            )

                        st.session_state.pending_payments.pop(token, None)
                        generated_tokens = st.session_state.setdefault("last_generated_tokens", [])
                        if token.upper() not in generated_tokens:
                            generated_tokens.append(token.upper())
                        st.success(f"{token} report generated.")
                        st.rerun()
                    except PaymentVerificationError as e:
                        st.error(f"Payment not verified: {e}")
                    except IntegrityError:
                        st.error("This transaction hash has already been used to unlock a report.")
                    except Exception as e:
                        st.error(f"Report generation failed after payment was confirmed: {e}")

    # AI Investment Brief - shown after a successful generation (persists across rerenders via session_state)
    if st.session_state.get("last_generated_tokens"):
        st.divider()
        st.subheader("AI Investment Brief")

        for token in st.session_state.last_generated_tokens:
            st.markdown(f"**{token}**")
            report_path = os.path.join(root_path, "reports", f"{token}_audit_report.md")
            report_text = load_md(report_path) if os.path.exists(report_path) else ""
            brief_key_haiku = f"brief_{token}_{HAIKU}"
            brief_key_sonnet = f"brief_{token}_{SONNET}"
            brief_key_opus = f"brief_{token}_{OPUS}"

            audience_gen = st.text_input(
                "Who is this brief for? (optional)",
                placeholder="e.g. my own use / cohort member / newsletter reader",
                key=f"audience_gen_{token}",
            )
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button(f"Generate Brief - Haiku ({token})", key=f"haiku_gen_{token}"):
                    with st.spinner("Generating via Haiku..."):
                        try:
                            brief, cost = generate_anthropic_brief(token, {}, report_text, model=HAIKU, audience_context=audience_gen)
                            st.session_state[brief_key_haiku] = (brief, cost)
                            st.session_state.pop(brief_key_sonnet, None)
                            st.session_state.pop(brief_key_opus, None)
                        except Exception as e:
                            st.error(f"Haiku error: {e}")
            with col_b:
                if st.button(f"Deep Analysis - Sonnet ({token})", key=f"sonnet_gen_{token}"):
                    with st.spinner("Generating via Sonnet..."):
                        try:
                            brief, cost = generate_anthropic_brief(token, {}, report_text, model=SONNET, audience_context=audience_gen)
                            st.session_state[brief_key_sonnet] = (brief, cost)
                            st.session_state.pop(brief_key_opus, None)
                        except Exception as e:
                            st.error(f"Sonnet error: {e}")
            with col_c:
                if st.button(f"Maximum Depth - Opus ({token})", key=f"opus_gen_{token}"):
                    with st.spinner("Generating via Opus..."):
                        try:
                            brief, cost = generate_anthropic_brief(token, {}, report_text, model=OPUS, audience_context=audience_gen)
                            st.session_state[brief_key_opus] = (brief, cost)
                        except Exception as e:
                            st.error(f"Opus error: {e}")

            # Display priority: Opus > Sonnet > Haiku
            display_brief, display_cost, display_model = None, None, None
            if brief_key_opus in st.session_state:
                display_brief, display_cost = st.session_state[brief_key_opus]
                display_model = "Opus"
            elif brief_key_sonnet in st.session_state:
                display_brief, display_cost = st.session_state[brief_key_sonnet]
                display_model = "Sonnet"
            elif brief_key_haiku in st.session_state:
                display_brief, display_cost = st.session_state[brief_key_haiku]
                display_model = "Haiku"

            if display_brief:
                st.markdown(display_brief)
                st.metric(label=f"Estimated cost ({display_model})", value=f"${display_cost:.6f}")

elif page.startswith("Blueprint:"):
    blueprint_name = page.split(": ")[1].lower().replace(" ", "-") + ".md"
    md_path = os.path.join(blueprints_dir, blueprint_name)
    md = load_md(md_path)
    st.markdown(md)
    st.divider()
    md_to_pdf(md, f"{blueprint_name.replace('.md','')}.pdf")

elif page.startswith("Report:"):
    token_name = page.split(": ")[1].upper()
    
    # Find the matching relative path from the pre-computed report_files list
    matching_rel_path = None
    for f in report_files:
        d_name = os.path.dirname(f)
        b_name = os.path.basename(f)
        t_name = os.path.basename(d_name).upper() if d_name else b_name.split('_')[0].upper()
        if t_name == token_name:
            matching_rel_path = f
            break
    
    if matching_rel_path:
        report_path = os.path.join(reports_dir, matching_rel_path)
        raw_md = load_md(report_path)
        metadata, md = extract_metadata_frontmatter(raw_md)

        if st.button("← Back to Overview", key="back_btn"):
            st.session_state.selected_page = "Overview"
            st.rerun()

        # Extract and display Blueprint Score + Verdict prominently
        score = int(metadata.get("Score", extract_blueprint_score(md)))
        verdict = metadata.get("Verdict", extract_final_verdict(md))
        if verdict == "Unknown" and score > 0:
            verdict = infer_verdict_from_score(score)
        screenshot = metadata.get("Screenshot", "None")
        
        score_emoji, score_delta_colour = extract_score_colour(score)
        verdict_emoji = extract_verdict_emoji(verdict)

        # Header row with score and verdict
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.metric(
                label=f"{score_emoji} Blueprint Score",
                value=f"{score}/100",
            )
        with col2:
            st.markdown(f"### {verdict_emoji} {verdict}")
            st.caption("Final Verdict")
        with col3:
            # Last updated timestamp
            mod_time = os.path.getmtime(os.path.join(os.getcwd(), report_path))
            mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%d %b %Y, %H:%M")
            st.caption(f"Last updated: {mod_date}")

        # Kill Switch warning
        if score < 20:
            st.error("🚨 **KILL SWITCH TRIGGERED** - Blueprint Score is below 20. One or more critical red flags have been detected. Review the Kill Switch section for details.")

        st.divider()

        # ---- View toggle: Investment Brief vs Full Report ----
        brief_key_haiku = f"brief_{token_name}_{HAIKU}"
        brief_key_sonnet = f"brief_{token_name}_{SONNET}"
        brief_key_opus = f"brief_{token_name}_{OPUS}"

        # Display priority: Opus > Sonnet > Haiku
        display_brief, display_cost, display_model = None, None, None
        if brief_key_opus in st.session_state:
            display_brief, display_cost = st.session_state[brief_key_opus]
            display_model = "Opus"
        elif brief_key_sonnet in st.session_state:
            display_brief, display_cost = st.session_state[brief_key_sonnet]
            display_model = "Sonnet"
        elif brief_key_haiku in st.session_state:
            display_brief, display_cost = st.session_state[brief_key_haiku]
            display_model = "Haiku"

        view_key = f"view_mode_{token_name}"
        if view_key not in st.session_state:
            st.session_state[view_key] = "Investment Brief" if display_brief else "Full Report"

        view_mode = st.radio(
            "View",
            ["Investment Brief", "Full Report"],
            index=0 if st.session_state[view_key] == "Investment Brief" else 1,
            horizontal=True,
            key=view_key,
            label_visibility="collapsed",
        )

        st.divider()

        if view_mode == "Investment Brief":
            with st.container(border=True):
                st.markdown("#### AI Investment Brief")
                audience_input = st.text_input(
                    "Who is this brief for? (optional)",
                    placeholder="e.g. my own use / cohort member new to DeFi / newsletter reader",
                    key=f"audience_{token_name}",
                )
                col_h, col_s, col_o = st.columns(3)
                with col_h:
                    if st.button("Generate - Haiku", key=f"rpt_haiku_{token_name}", use_container_width=True):
                        with st.spinner("Generating via Haiku..."):
                            try:
                                brief, cost = generate_anthropic_brief(token_name, {}, md, model=HAIKU, audience_context=audience_input)
                                st.session_state[brief_key_haiku] = (brief, cost)
                                st.session_state.pop(brief_key_sonnet, None)
                                st.session_state.pop(brief_key_opus, None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Haiku error: {e}")
                with col_s:
                    if st.button("Deep Analysis - Sonnet", key=f"rpt_sonnet_{token_name}", use_container_width=True):
                        with st.spinner("Generating via Sonnet..."):
                            try:
                                brief, cost = generate_anthropic_brief(token_name, {}, md, model=SONNET, audience_context=audience_input)
                                st.session_state[brief_key_sonnet] = (brief, cost)
                                st.session_state.pop(brief_key_opus, None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Sonnet error: {e}")
                with col_o:
                    if st.button("Maximum Depth - Opus", key=f"rpt_opus_{token_name}", use_container_width=True):
                        with st.spinner("Generating via Opus..."):
                            try:
                                brief, cost = generate_anthropic_brief(token_name, {}, md, model=OPUS, audience_context=audience_input)
                                st.session_state[brief_key_opus] = (brief, cost)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Opus error: {e}")

                if display_brief:
                    st.markdown(display_brief)
                    st.caption(f"Model: {display_model} | Estimated cost: ${display_cost:.6f}")
                else:
                    st.info("Click a button above to generate a plain-English brief from this report.")

        else:
            sections = split_report_phases(md)
            tab_names = [k for k in sections.keys() if sections[k].strip()]

            if len(tab_names) > 1:
                phase_key = f"phase_idx_{token_name}"
                if phase_key not in st.session_state:
                    st.session_state[phase_key] = 0

                idx = min(st.session_state[phase_key], len(tab_names) - 1)

                nav_left, nav_centre, nav_right = st.columns([1, 4, 1])
                with nav_left:
                    if st.button("← Previous", key=f"prev_{token_name}", disabled=(idx == 0), use_container_width=True):
                        st.session_state[phase_key] = idx - 1
                        st.rerun()
                with nav_centre:
                    st.markdown(
                        f"<p style='text-align:center; font-weight:600; margin:0.4rem 0;'>"
                        f"{tab_names[idx]}&nbsp;&nbsp;"
                        f"<span style='opacity:0.5; font-weight:400;'>({idx + 1} of {len(tab_names)})</span>"
                        f"</p>",
                        unsafe_allow_html=True,
                    )
                with nav_right:
                    if st.button("Next →", key=f"next_{token_name}", disabled=(idx == len(tab_names) - 1), use_container_width=True):
                        st.session_state[phase_key] = idx + 1
                        st.rerun()

                st.divider()

                scroll_key = f"scroll_top_{token_name}"
                if st.session_state.pop(scroll_key, False):
                    import streamlit.components.v1 as components
                    components.html(
                        "<script>window.scrollTo(0,0); window.parent.scrollTo(0,0);</script>",
                        height=0,
                    )

                current_name = tab_names[idx]
                st.markdown(clean_report_for_display(sections[current_name]), unsafe_allow_html=True)
                if "Phase 4" in current_name and screenshot and screenshot != "None" and os.path.exists(screenshot):
                    st.image(screenshot, caption=f"DexScreener Live Chart Capture for {token_name.upper()}")

                if len(sections[current_name]) >= 1500:
                    st.divider()
                    bnav_left, bnav_centre, bnav_right = st.columns([1, 4, 1])
                    with bnav_left:
                        if st.button("← Previous", key=f"prev_bot_{token_name}", disabled=(idx == 0), use_container_width=True):
                            st.session_state[phase_key] = idx - 1
                            st.session_state[scroll_key] = True
                            st.rerun()
                    with bnav_centre:
                        st.markdown(
                            f"<p style='text-align:center; font-weight:600; margin:0.4rem 0;'>"
                            f"{tab_names[idx]}&nbsp;&nbsp;"
                            f"<span style='opacity:0.5; font-weight:400;'>({idx + 1} of {len(tab_names)})</span>"
                            f"</p>",
                            unsafe_allow_html=True,
                        )
                    with bnav_right:
                        if st.button("Next →", key=f"next_bot_{token_name}", disabled=(idx == len(tab_names) - 1), use_container_width=True):
                            st.session_state[phase_key] = idx + 1
                            st.session_state[scroll_key] = True
                            st.rerun()
            else:
                st.markdown(clean_report_for_display(md), unsafe_allow_html=True)

        st.divider()
        md_to_pdf(md, f"{token_name}-audit-latest.pdf")
    else:
        st.error("Report file not found. Generate a report first.")