"""Markdown report to PDF, for the download button."""
from io import BytesIO

import markdown
from xhtml2pdf import pisa

_STYLE = """
@page { size: a4; margin: 1.5cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.4; color: rgb(33,33,33); }
h1 { font-size: 16pt; border-bottom: 2pt solid rgb(200,200,200); padding-bottom: 4pt; }
h2 { font-size: 13pt; margin-top: 14pt; }
h3 { font-size: 11pt; margin-top: 10pt; }
blockquote { border-left: 2pt solid rgb(11,87,201); padding-left: 6pt; color: rgb(60,60,60); }
table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 8.5pt; }
td, th { border: 0.5pt solid rgb(180,180,180); padding: 4pt 3pt; text-align: left; vertical-align: top; }
th { background-color: rgb(240,240,240); }
"""


def markdown_to_pdf(md_text):
    """Return (pdf_bytes, error). error is None on success."""
    body = markdown.markdown(md_text, extensions=["extra", "tables"])
    html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{_STYLE}</style></head><body>{body}</body></html>'
    buffer = BytesIO()
    status = pisa.CreatePDF(html, dest=buffer)
    if status.err:
        return None, f"The PDF could not be built ({status.err} errors). Download the markdown instead."
    return buffer.getvalue(), None
