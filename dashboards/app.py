import streamlit as st
import os
import sys
import re
import datetime
import markdown
import html
from xhtml2pdf import pisa
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Import the report generator
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
from report_generator import generate_report, extract_blueprint_score, extract_final_verdict

st.set_page_config(page_title="ABC Research Dashboard", layout="wide")

# Professional large title
st.markdown("""
<h1 style='font-size: 3em; text-align: center; margin-bottom: 0.5em;'>
Africa's Blockchain Club Research Dashboard
</h1>
""", unsafe_allow_html=True)

st.caption("Liquidity-First Blueprints & Reports | Live PDF Generation (Professional)")

# Sidebar
st.sidebar.header("Blueprints & Reports")

if not os.path.exists("blueprints"): os.makedirs("blueprints")
if not os.path.exists("reports"): os.makedirs("reports")

blueprint_files = [f for f in os.listdir("blueprints") if f.endswith(".md")]

# Only show report folders that actually contain an audit-latest.md file
report_folders = []
for d in os.listdir("reports"):
    folder_path = os.path.join("reports", d)
    if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, "audit-latest.md")):
        report_folders.append(d)

page = st.sidebar.radio("Select",
    ["Overview", "Generate Report"] +
    [f"Blueprint: {f.replace('.md','').replace('-',' ').title()}" for f in blueprint_files] +
    [f"Report: {folder.upper()}" for folder in report_folders]
)


# ====================== PDF GENERATOR ======================
def clean_markdown_for_pdf(md_text):
    md_text = md_text.replace('■', '-')
    md_text = md_text.replace('•', '-')
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
            @page {{ size: a4; margin: 2cm 2.5cm; }}
            body {{ font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.4; color: rgb(33, 33, 33); }}
            h1 {{ font-size: 16pt; font-weight: bold; margin-top: 0; margin-bottom: 12pt; color: rgb(0,0,0); border-bottom: 2pt solid rgb(200,200,200); padding-bottom: 4pt; }}
            h2 {{ font-size: 13pt; font-weight: bold; margin-top: 14pt; margin-bottom: 8pt; color: rgb(51,51,51); }}
            h3 {{ font-size: 11pt; font-weight: bold; margin-top: 10pt; margin-bottom: 6pt; color: rgb(68,68,68); }}
            p {{ margin-bottom: 6pt; text-align: justify; }}
            ul, ol {{ margin-left: 12pt; margin-bottom: 8pt; padding-left: 8pt; }}
            li {{ margin-bottom: 4pt; line-height: 1.5; }}
            table {{ width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 9pt; }}
            td, th {{ border: 1pt solid rgb(187,187,187); padding: 4pt 6pt; text-align: left; vertical-align: top; }}
            th {{ background-color: rgb(235,235,235); font-weight: bold; text-align: center; }}
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


def split_report_phases(md_text):
    """Split report markdown into phase sections for tabbed display"""
    sections = {}
    current_key = "Overview"
    current_lines = []

    for line in md_text.split("\n"):
        # Detect Phase headers or Kill Switch or Model Comparison
        if re.match(r'^##\s+Phase\s+1', line, re.IGNORECASE):
            sections[current_key] = "\n".join(current_lines)
            current_key = "Phase 1: Supply"
            current_lines = [line]
        elif re.match(r'^##\s+Phase\s+2', line, re.IGNORECASE):
            sections[current_key] = "\n".join(current_lines)
            current_key = "Phase 2: Liquidity"
            current_lines = [line]
        elif re.match(r'^##\s+Phase\s+3', line, re.IGNORECASE):
            sections[current_key] = "\n".join(current_lines)
            current_key = "Phase 3: Derivatives"
            current_lines = [line]
        elif re.match(r'^##\s+Phase\s+4', line, re.IGNORECASE):
            sections[current_key] = "\n".join(current_lines)
            current_key = "Phase 4: Synthesis"
            current_lines = [line]
        elif re.match(r'^##\s+Red\s+Flag|^##\s+Kill\s+Switch', line, re.IGNORECASE):
            sections[current_key] = "\n".join(current_lines)
            current_key = "Kill Switch"
            current_lines = [line]
        elif re.match(r'^##\s+AI\s+Model\s+Comparison', line, re.IGNORECASE):
            sections[current_key] = "\n".join(current_lines)
            current_key = "Model Comparison"
            current_lines = [line]
        elif re.match(r'^##\s+Source', line, re.IGNORECASE):
            sections[current_key] = "\n".join(current_lines)
            current_key = "Sources"
            current_lines = [line]
        else:
            current_lines.append(line)

    sections[current_key] = "\n".join(current_lines)
    return sections


# ====================== MAIN LOGIC ======================
if page == "Overview":
    st.success("✅ Dashboard is running")
    st.info("Click **Generate Report** to create new professional audits using live data and your blueprint.")
    st.markdown("""
    #### Features
    - Full blueprint-following AI reports (British English, institutional grade)
    - **All AI models compete** — best Blueprint Score wins
    - Live CoinGecko + Coinglass data with Kill Switch analysis
    - Embedded charts & professional PDF export
    - Model comparison appended to every report
    """)

elif page == "Generate Report":
    st.header("Generate New Forensic Audit")
    st.info("All 3 AI models (OpenRouter, Gemini, Grok) will generate reports. The one with the **highest Blueprint Score** is saved. Reports always overwrite the previous version to stay current.")

    col1, col2 = st.columns([2, 1])
    with col1:
        tokens = st.multiselect("Select Tokens", ["BTC", "ETH"], default=["BTC", "ETH"])
    with col2:
        custom_token = st.text_input("Or enter a custom token ID", placeholder="e.g., solana, cardano")

    date = st.date_input("Report Date", datetime.date.today())

    # Merge custom token
    all_tokens = [t.lower() for t in tokens]
    if custom_token.strip():
        all_tokens.append(custom_token.strip().lower())

    if st.button("🚀 Generate Reports", type="primary"):
        if not all_tokens:
            st.warning("Please select or enter at least one token.")
        else:
            generated = []
            for token in all_tokens:
                with st.spinner(f"⏳ Fetching live data + running all AI models for **{token.upper()}**..."):
                    try:
                        path = generate_report(token, date.isoformat())
                        generated.append((token, path))
                        st.success(f"✅ {token.upper()} report generated and saved!")
                    except Exception as e:
                        st.error(f"❌ Error generating {token.upper()}: {e}")
            if generated:
                st.success(f"✅ Successfully generated {len(generated)} report(s)! Refreshing sidebar...")
                st.rerun()

elif page.startswith("Blueprint:"):
    blueprint_name = page.split(": ")[1].lower().replace(" ", "-") + ".md"
    md_path = os.path.join("blueprints", blueprint_name)
    md = load_md(md_path)
    st.markdown(md)
    st.divider()
    md_to_pdf(md, f"{blueprint_name.replace('.md','')}.pdf")

elif page.startswith("Report:"):
    token_name = page.split(": ")[1].lower()
    report_path = os.path.join("reports", token_name, "audit-latest.md")

    if os.path.exists(report_path):
        md = load_md(report_path)

        # Extract and display Blueprint Score + Verdict prominently
        score = extract_blueprint_score(md)
        verdict = extract_final_verdict(md)
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
            st.error("🚨 **KILL SWITCH TRIGGERED** — Blueprint Score is below 20. One or more critical red flags have been detected. Review the Kill Switch section for details.")

        st.divider()

        # Tabbed phase navigation
        sections = split_report_phases(md)
        tab_names = [k for k in sections.keys() if sections[k].strip()]

        if len(tab_names) > 1:
            tabs = st.tabs(tab_names)
            for tab, name in zip(tabs, tab_names):
                with tab:
                    st.markdown(sections[name], unsafe_allow_html=True)
        else:
            # Fallback: show full report
            st.markdown(md, unsafe_allow_html=True)

        st.divider()
        md_to_pdf(md, f"{token_name}-audit-latest.pdf")
    else:
        st.error("Report file not found. Generate a report first.")