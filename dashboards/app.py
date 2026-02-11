import streamlit as st
from fpdf import FPDF
import markdown2
import os

st.set_page_config(page_title="ABC Research Dashboard", layout="wide")
st.title("🔬 Africa’s Blockchain Club Research Dashboard")
st.caption("Liquidity-First Blueprints & Reports | Live PDF Generation")

# Sidebar for navigation (auto-discovers blueprints)
st.sidebar.header("Blueprints & Reports")
blueprint_files = [f for f in os.listdir("blueprints") if f.endswith(".md")]
report_folders = [d for d in os.listdir("reports") if os.path.isdir(os.path.join("reports", d))]

page = st.sidebar.radio("Select", 
    ["Overview"] + 
    [f"Blueprint: {f.replace('.md','').replace('-',' ').title()}" for f in blueprint_files] +
    [f"Report: {folder.title()}" for folder in report_folders]
)

def md_to_pdf(md_text, filename):
    html = markdown2.markdown(md_text)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in html.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    st.download_button(f"📥 Download {filename}", pdf_bytes, filename, "application/pdf")

def load_md(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "# Not found"

if page == "Overview":
    st.success("Select a blueprint or report from sidebar. PDFs generated live — no bloat in repo.")
    st.info("Add new tasks by creating files in blueprints/ with naming: task-name-blueprint-v1.0.md")

elif page.startswith("Blueprint:"):
    blueprint_name = page.split(": ")[1].lower().replace(" ", "-") + ".md"
    md = load_md(f"blueprints/{blueprint_name}")
    st.markdown(md)
    st.divider()
    md_to_pdf(md, f"{blueprint_name.replace('.md','')}.pdf")

elif page.startswith("Report:"):
    folder = page.split(": ")[1].lower().replace(" ", "-")
    # Simple: show all .md in that folder
    report_path = f"reports/{folder}"
    if os.path.exists(report_path):
        for file in os.listdir(report_path):
            if file.endswith(".md"):
                md = load_md(f"{report_path}/{file}")
                st.subheader(file.replace(".md", "").title())
                st.markdown(md)
                st.divider()
                md_to_pdf(md, f"{file.replace('.md','')}.pdf")