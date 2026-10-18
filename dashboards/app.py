"""
Entry point: streamlit run dashboards/app.py

Sets up the page, the theme and the top navigation, then hands over to the
view for the chosen page. Screens follow the job in the order a learner does
it: start at Home, research a token, read the reports, then the worked
example and the method behind it.
"""
import logging
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

import db  # noqa: E402
from config import ROOT_DIR, SETTINGS  # noqa: E402
from dashboards.ui.components import footer  # noqa: E402
from dashboards.ui.theme import apply_theme  # noqa: E402
from dashboards.views import attack_cost, home, method, reports, research  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

LOGO_PATH = ROOT_DIR / "dashboards" / "static" / "logo.svg"


def _logo_svg():
    """The brand tile: the brand initials on the accent colour, with the
    corner-cut notch from the front-end standard. Drawn from config so a fork
    needs no image file."""
    accent = escape(SETTINGS.brand_accent)
    initials = escape(SETTINGS.brand_short[:4])
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" role="img" '
        f'aria-label="{escape(SETTINGS.brand_name)}">'
        f'<polygon points="7,0 40,0 40,40 0,40 0,9" fill="{accent}"/>'
        f'<text x="20" y="25" text-anchor="middle" font-family="Figtree, Arial, sans-serif" '
        f'font-size="12" font-weight="800" fill="#ffffff">{initials}</text>'
        "</svg>"
    )


def _write_logo():
    svg = _logo_svg()
    LOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOGO_PATH.exists() or LOGO_PATH.read_text(encoding="utf-8") != svg:
        LOGO_PATH.write_text(svg, encoding="utf-8")


st.set_page_config(
    page_title=SETTINGS.app_name,
    page_icon=str(ROOT_DIR / "dashboards" / "static" / "abc-logo-tile-180.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_theme()
# The ABC logo tile when it is present; a fork without it gets a tile drawn from config
BRAND_LOGO = ROOT_DIR / "dashboards" / "static" / "abc-logo-tile.png"
if BRAND_LOGO.exists():
    st.logo(str(BRAND_LOGO), size="large", link=None)
else:
    _write_logo()
    st.logo(str(LOGO_PATH), size="large", link=None)
db.init_db()

pages = [
    st.Page(home.render, title="Home", icon=":material/home:", url_path="home", default=True),
    st.Page(research.render, title="Research a token", icon=":material/search:", url_path="research"),
    st.Page(reports.render, title="Reports", icon=":material/description:", url_path="reports"),
    st.Page(attack_cost.render, title="Attack cost", icon=":material/shield:", url_path="attack-cost"),
    st.Page(method.render, title="How it works", icon=":material/info:", url_path="how-it-works"),
]
st.navigation(pages, position="top").run()
footer()
