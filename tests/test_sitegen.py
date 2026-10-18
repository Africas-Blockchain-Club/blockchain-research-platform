import pytest

from data_analytics.risk_profile import compute_risk_checks
from sitegen import build as sitegen
from tools import report_store

EVIL = (
    "# EXM Blockchain Research Report\n\n## Phase 0: The Blockchain\n\n"
    "<script>alert('x')</script>\n\n[click me](javascript:alert(1))\n\n[docs](https://example.org)\n"
)


@pytest.fixture
def site(temp_store, data_summary, tmp_path, monkeypatch):
    monkeypatch.setattr(sitegen, "PDF_CACHE", tmp_path / "pdf-cache")
    monkeypatch.setattr(sitegen, "NETWORK_DIR", tmp_path / "network")
    report_store.save_report("EXM", EVIL, mode=report_store.MODE_DATA, model=None,
                             risk_checks=compute_risk_checks(data_summary), data_summary=data_summary)
    return sitegen.build_site(tmp_path / "site")


def test_every_page_is_built(site):
    for path in ("index.html", "blockchains/index.html", "blockchains/bitcoin.html", "blockchains/hyperliquid.html",
                 "reports/index.html", "reports/EXM.html", "reports/EXM.md", "how-it-works.html", "404.html",
                 "static/abc-shell.css", "static/wtc-shell.js"):
        assert (site / path).exists(), path


def test_risk_counts_render_as_numbers(site):
    page = (site / "reports" / "EXM.html").read_text()
    assert "built-in method" not in page
    assert '<span class="v">' in page


def test_report_html_and_script_links_are_neutralised(site):
    page = (site / "reports" / "EXM.html").read_text()
    assert "<script>alert" not in page
    assert "javascript:" not in page
    assert 'href="https://example.org"' in page


def test_pages_load_no_inline_scripts(site):
    # The content security policy forbids inline scripts; every script must be a file
    for page in site.rglob("*.html"):
        html = page.read_text()
        assert "<script>" not in html and "onclick=" not in html, page
