import streamlit as st
import os
import re
import markdown
import html
from xhtml2pdf import pisa
from io import BytesIO

st.set_page_config(page_title="ABC Research Dashboard", layout="wide")
st.title("Africa's Blockchain Club Research Dashboard")
st.caption("Liquidity-First Blueprints & Reports | Live PDF Generation (Professional)")

## Sidebar navigation
st.sidebar.header("Blueprints & Reports")
## Ensure directories exist to prevent errors if empty
if not os.path.exists("blueprints"): os.makedirs("blueprints")
if not os.path.exists("reports"): os.makedirs("reports")

blueprint_files = [f for f in os.listdir("blueprints") if f.endswith(".md")]
report_folders = [d for d in os.listdir("reports") if os.path.isdir(os.path.join("reports", d))]

page = st.sidebar.radio("Select", 
    ["Overview"] + 
    [f"Blueprint: {f.replace('.md','').replace('-',' ').title()}" for f in blueprint_files] +
    [f"Report: {folder.title()}" for folder in report_folders]
)

## ENHANCED PDF GENERATOR ---
def clean_markdown_for_pdf(md_text):
    """Clean markdown content for better PDF rendering"""
    ## Fix problematic characters before conversion
    md_text = md_text.replace('■', '-')  ## Fix bullet points
    md_text = md_text.replace('•', '-')  ## Fix bullet points
    md_text = md_text.replace('"', '"').replace('"', '"')  ## Smart quotes
    md_text = md_text.replace(''', "'").replace(''', "'")  ## Smart apostrophes
    return md_text

def md_to_pdf(md_text, filename):
    ## 1. Clean markdown first
    md_text = clean_markdown_for_pdf(md_text)
    
    ## 2. Convert Markdown to HTML
    html_content = markdown.markdown(md_text, extensions=['extra', 'tables'])
    
    ## 3. Decode any existing HTML entities to prevent double-encoding
    html_content = html.unescape(html_content)
    
    ## 4. FIXED: Use proper HTML entities (not broken ones)
    ## Remove the problematic replacements that were causing &###36; issues
    html_content = html_content.replace('±', '&plusmn;')
    html_content = html_content.replace('→', '&rarr;')
    html_content = html_content.replace('—', '&mdash;')
    html_content = html_content.replace('–', '&ndash;')
    
    ## Keep $ and % as regular characters - they work fine in xhtml2pdf
    ## html_content = html_content.replace('$', '&##36;')  ## REMOVED
    ## html_content = html_content.replace('%', '&##37;')  ## REMOVED
    
    ## 5. Enhanced CSS with better table styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ 
                size: a4; 
                margin: 2cm 2.5cm; 
            }}
            body {{ 
                font-family: Arial, Helvetica, sans-serif; 
                font-size: 10pt; 
                line-height: 1.4; 
                color: rgb(33, 33, 33); 
            }}
            
            h1 {{ 
                font-size: 16pt; 
                font-weight: bold; 
                margin-top: 0pt;
                margin-bottom: 12pt; 
                color: rgb(0, 0, 0);
                border-bottom: 2pt solid rgb(200, 200, 200);
                padding-bottom: 4pt;
            }}
            
            h2 {{ 
                font-size: 13pt; 
                font-weight: bold; 
                margin-top: 14pt; 
                margin-bottom: 8pt; 
                color: rgb(51, 51, 51);
            }}
            
            h3 {{ 
                font-size: 11pt; 
                font-weight: bold; 
                margin-top: 10pt; 
                margin-bottom: 6pt; 
                color: rgb(68, 68, 68);
            }}
            
            p {{ 
                margin-bottom: 6pt; 
                text-align: justify;
                text-justify: inter-word;
            }}
            
            ul, ol {{ 
                margin-left: 12pt; 
                margin-bottom: 8pt;
                padding-left: 8pt;
            }}
            
            li {{ 
                margin-bottom: 4pt; 
                line-height: 1.5;
                text-align: left;
            }}
            
            strong {{ 
                font-weight: bold; 
                color: rgb(0, 0, 0);
            }}
            
            em {{ 
                font-style: italic; 
            }}
            
            code {{
                font-family: Courier, monospace;
                font-size: 9pt;
                background-color: rgb(245, 245, 245);
                padding: 1pt 3pt;
                border: 1pt solid rgb(220, 220, 220);
            }}
            
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 8pt 0;
                font-size: 9pt;
            }}
            
            td, th {{ 
                border: 1pt solid rgb(187, 187, 187); 
                padding: 4pt 6pt;
                text-align: left;
                vertical-align: top;
            }}
            
            th {{
                background-color: rgb(235, 235, 235);
                font-weight: bold;
                text-align: center;
            }}
            
            tr:nth-child(even) {{
                background-color: rgb(250, 250, 250);
            }}
            
            hr {{
                border: none;
                border-top: 1pt solid rgb(204, 204, 204);
                margin: 12pt 0;
            }}
            
            /* Links */
            a {{
                color: rgb(0, 102, 204);
                text-decoration: underline;
            }}
            
            /* Blockquotes */
            blockquote {{
                margin: 8pt 0;
                padding: 6pt 12pt;
                border-left: 3pt solid rgb(204, 204, 204);
                background-color: rgb(248, 248, 248);
                font-style: italic;
            }}
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
        st.error(f"PDF generation encountered {pisa_status.err} errors.")
        
    st.download_button(
        label=f"📄 Download {filename}",
        data=pdf_buffer.getvalue(),
        file_name=filename,
        mime="application/pdf",
        help="Download professionally formatted PDF report"
    )


def load_md(path):
    full_path = os.path.join(os.getcwd(), path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return "## File not found – check path"

## --- MAIN LOGIC ---

if page == "Overview":
    st.success("✅ Dashboard running. Engine upgraded to HTML-based PDF generation.")
    st.info("📊 Reports now support UTF-8, proper formatting, and professional styling.")
    st.markdown("""
    #### Features:
    - **Liquidity-aware token analysis blueprints**
    - **Professional PDF export** with proper typography
    - **Multi-report support** for comprehensive research
    - **Enhanced table formatting** and clean symbol rendering
    - **Fixed HTML entity issues** for professional output
    """)

elif page.startswith("Blueprint:"):
    blueprint_name = page.split(": ")[1].lower().replace(" ", "-") + ".md"
    md_path = os.path.join("blueprints", blueprint_name)
    md = load_md(md_path)
    st.markdown(md)
    st.divider()
    md_to_pdf(md, f"{blueprint_name.replace('.md','')}.pdf")

elif page.startswith("Report:"):
    folder = page.split(": ")[1].lower().replace(" ", "-")
    report_dir = os.path.join("reports", folder)
    if os.path.exists(report_dir):
        files = sorted([f for f in os.listdir(report_dir) if f.endswith(".md")])
        if files:
            for file in files:
                md_path = os.path.join(report_dir, file)
                md = load_md(md_path)
                st.subheader(file.replace(".md", "").replace("-", " ").title())
                st.markdown(md)
                st.divider()
                md_to_pdf(md, f"{folder}-{file.replace('.md','')}.pdf")
        else:
            st.warning("No markdown files found in this report folder.")
    else:
        st.error("Report folder not found")
