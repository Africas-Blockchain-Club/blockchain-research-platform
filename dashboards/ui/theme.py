"""
The visual layer: colour tokens, type and layout, applied over Streamlit.

Follows the ABC front-end standard (~/.claude/skills/abc-frontend-standard):
the structure, layout and accessibility rules of the WeThinkCode_ front-end
standard, with the look of africasblockchainclub.com - dark first, one amber
accent, Geist, glass cards, the ABC logo tile, the elephant mascot and the
home video loop. The accents come from config so a fork can rebrand.

Streamlit draws its own page, so three rules are met in a Streamlit way
rather than copied (see docs/FRONTEND.md):
- the theme follows Streamlit's own light/dark setting (st.context.theme),
  falling back to the operating system preference, dark when there is none;
- navigation is Streamlit's top navigation bar, not the shell's menu;
- the public pages (home, blockchains, reports) are the static site in
  sitegen/; this app keeps only live research and the attack cost page.
"""
import streamlit as st

from config import SETTINGS

# Every text pairing checked against WCAG AA on 18 October 2026 (abc-brand.md)
_LIGHT = {
    "bg": "#fafafa", "surface": "#ffffff", "wash": "#f5f5f4", "line": "#e5e5e5", "line-strong": "#d4d4d4",
    "text": "#171717", "head": "#0a0a0a", "muted": "#404040", "subtle": "#525252",
    "on-blue": "#ffffff", "blue-wash": "#fff4e0",
    "band-a": "#0a0a0a", "band-b": "#7b3306", "band-text": "#fde68a",
    "pass": "#15803d", "pass-wash": "#e8f5ee", "warn": "#a15c00", "warn-wash": "#fff4e0",
    "stop": "#b91c1c", "stop-wash": "#fdecea",
    "glass": "rgba(10,10,10,0.03)", "glass-line": "rgba(10,10,10,0.10)",
    "glow": "rgba(249,156,0,0.25)", "shadow": "0 10px 25px -8px rgba(10,10,10,0.15)",
    "w-light": "300", "w-display": "800", "track-body": "0", "track-display": "-0.02em", "lh-body": "1.55",
}
_DARK = {
    "bg": "#0a0a0a", "surface": "#171717", "wash": "#262626", "line": "rgba(255,255,255,0.12)", "line-strong": "#404040",
    "text": "#f5f5f5", "head": "#ffffff", "muted": "#d4d4d4", "subtle": "#a3a3a3",
    "on-blue": "#0a0a0a", "blue-wash": "#2a1d05",
    "band-a": "#0a0a0a", "band-b": "#7b3306", "band-text": "#fde68a",
    "pass": "#4ade80", "pass-wash": "#0f2a1a", "warn": "#fcbb00", "warn-wash": "#2a1d05",
    "stop": "#f87171", "stop-wash": "#2d1414",
    "glass": "rgba(255,255,255,0.06)", "glass-line": "rgba(255,255,255,0.18)",
    "glow": "rgba(249,156,0,0.35)", "shadow": "0 25px 50px -12px rgba(0,0,0,0.6)",
    "w-light": "400", "w-display": "800", "track-body": "0.005em", "track-display": "-0.02em", "lh-body": "1.6",
}


def _vars(tokens, accent):
    body = "".join(f"--{name}:{value};" for name, value in tokens.items())
    return f"{body}--blue:{accent};"


def _token_css():
    light = _vars(_LIGHT, SETTINGS.brand_accent)
    dark = _vars(_DARK, SETTINGS.brand_accent_dark)
    theme_type = getattr(getattr(st.context, "theme", None), "type", None)
    if theme_type == "dark":
        return f":root{{{dark}color-scheme:dark;}}"
    if theme_type == "light":
        return f":root{{{light}color-scheme:light;}}"
    # Streamlit has not reported a theme yet: dark first, as ABC is, unless the system asks for light
    return (
        f":root{{{dark}color-scheme:dark;}}"
        f"@media (prefers-color-scheme:light){{:root:not([data-theme=\"dark\"]){{{light}color-scheme:light;}}}}"
        f":root[data-theme=\"light\"]{{{light}color-scheme:light;}}"
    )


_CSS = """
html { overflow-y:scroll; }
body { overflow-x:clip; }
.stApp, header[data-testid="stHeader"] { background:var(--bg); color:var(--text); }
.stApp { font-family:"Geist","Helvetica Neue",Helvetica,Arial,sans-serif; }
.stApp, .stApp p, .stApp li { letter-spacing:var(--track-body); line-height:var(--lh-body); }

/* One centred 76rem column for every page, matching the top bar */
[data-testid="stMainBlockContainer"], .block-container {
  max-width:76rem; padding-left:clamp(1rem,4vw,2.5rem); padding-right:clamp(1rem,4vw,2.5rem);
  padding-top:5rem; padding-bottom:4rem;
}
/* Streamlit's top bar holds the logo and navigation; line it up with the column */
header[data-testid="stHeader"] {
  /* Streamlit pads the bar by 1rem itself, so subtract that to land on the column edge */
  padding-left:max(0px, calc((100vw - 76rem) / 2 + clamp(1rem,4vw,2.5rem) - 1rem));
  padding-right:max(0px, calc((100vw - 76rem) / 2 + clamp(1rem,4vw,2.5rem) - 1rem));
  border-bottom:1px solid var(--line);
}

/* Help text is read, not glanced at: at least 15px */
[data-testid="stCaptionContainer"], .stCaption, [data-testid="stWidgetLabel"] p { font-size:0.9375rem !important; }

/* Buttons: 48px pills, one accent colour for actions */
.stButton button, .stDownloadButton button, .stFormSubmitButton button, [data-testid="stPageLink"] a {
  min-height:48px; border-radius:999px; font-weight:600; padding-left:1.4rem; padding-right:1.4rem;
}
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {
  background:var(--blue); border-color:var(--blue); color:var(--on-blue);
}
.stButton button[kind="primary"]:hover { box-shadow:0 0 25px 4px var(--glow); }
.stButton button:disabled, .stFormSubmitButton button:disabled {
  background:var(--line-strong) !important; border-color:transparent !important; color:var(--muted) !important; cursor:not-allowed;
}
:focus-visible { outline:3px solid var(--blue) !important; outline-offset:2px; }

/* Inputs at least 48px tall */
[data-baseweb="input"], [data-baseweb="select"] > div { min-height:48px; }

/* Tabs scroll inside themselves, never the page */
[data-baseweb="tab-list"] { overflow-x:auto; scrollbar-width:none; }
[data-baseweb="tab"] { min-height:48px; font-weight:600; }

/* Markdown tables in reports fill the column and scroll inside themselves */
[data-testid="stMarkdownContainer"] table { width:100%; display:table; border-collapse:collapse; }
@media (max-width:719px) { [data-testid="stMarkdownContainer"] table { display:block; overflow-x:auto; } }
[data-testid="stMarkdownContainer"] th { font-size:0.8125rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--subtle); }
[data-testid="stMarkdownContainer"] blockquote { border-left:3px solid var(--blue); background:var(--wash); padding:0.75rem 1rem; border-radius:0 12px 12px 0; color:var(--text); }

/* Shared components */
.brp-kicker { font-size:0.75rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--subtle); }
.brp-head { display:grid; gap:0.4rem; margin:0.5rem 0 1rem; }
.brp-head h1 { margin:0; padding:0; color:var(--head); font-weight:800; font-size:clamp(1.75rem,4vw,2.5rem); line-height:1.1; }
.brp-head p { margin:0; color:var(--muted); font-weight:var(--w-light); font-size:clamp(1.0rem,2vw,1.15rem); }

.brp-grid { display:grid; gap:1rem; grid-template-columns:1fr; margin:0.5rem 0 1rem; }
@media (min-width:720px) { .brp-grid { grid-template-columns:repeat(2,1fr); } }
@media (min-width:1100px) { .brp-grid.three { grid-template-columns:repeat(3,1fr); } }
/* Glass cards, as on the ABC site; solid enough to read without backdrop-filter */
.brp-card { background:var(--glass); border:1px solid var(--glass-line); border-radius:16px; padding:clamp(1rem,3vw,1.5rem);
  backdrop-filter:blur(8px);
  display:flex; flex-direction:column; gap:0.6rem; color:var(--text); }
.brp-card h3 { margin:0; padding:0; font-size:1.125rem; font-weight:700; color:var(--head); }
.brp-card p { margin:0; color:var(--muted); font-size:0.9375rem; }
.brp-link { color:var(--blue) !important; font-weight:600; min-height:44px; display:inline-flex; align-items:center; text-decoration:none !important; }
.brp-link:hover { text-decoration:underline !important; }
.brp-card .brp-meta { font-size:0.875rem; color:var(--subtle); }
.brp-card.flagged { border-left:4px solid var(--warn); }
.brp-card.clear { border-left:4px solid var(--line-strong); }
.brp-card.no_data { border-left:4px dashed var(--line-strong); }

.brp-pill { display:inline-flex; align-items:center; gap:0.35rem; width:fit-content; font-size:0.8125rem; font-weight:700;
  padding:0.2rem 0.7rem; border-radius:999px; border:1px solid var(--line); background:var(--wash); color:var(--muted); }
.brp-pill.flagged { background:var(--warn-wash); color:var(--warn); border-color:transparent; }
.brp-pill.ai { background:var(--blue-wash); color:var(--blue); border-color:transparent; }

.brp-stats { display:grid; gap:0.75rem; grid-template-columns:repeat(3,1fr); margin:0.25rem 0 1rem; }
.brp-stat { background:var(--glass); border:1px solid var(--glass-line); border-radius:12px; padding:0.9rem 1rem; display:grid; gap:0.15rem; }
.brp-stat .v { font-size:1.75rem; font-weight:800; color:var(--head); font-variant-numeric:tabular-nums; }
.brp-stat .k { font-size:0.8125rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:var(--subtle); }

.brp-notice { border-radius:12px; padding:1rem 1.2rem; background:var(--blue-wash); color:var(--text); display:grid; gap:0.3rem; margin:0.5rem 0 1rem; }
.brp-notice .brp-kicker { color:var(--blue); }
.brp-notice p { margin:0; font-size:0.9375rem; }
.brp-notice.warn { background:var(--warn-wash); } .brp-notice.warn .brp-kicker { color:var(--warn); }

.brp-steps { counter-reset:step; }
.brp-steps .brp-card h3::before { counter-increment:step; content:counter(step) ". "; color:var(--blue); }

.brp-footer { border-top:1px solid var(--line); margin-top:3rem; padding-top:1.25rem; display:grid; gap:0.4rem;
  font-size:0.875rem; color:var(--subtle); }
.brp-footer p { margin:0; }
.brp-footer a { color:var(--blue); }

/* Sections fade and rise once; nothing moves for people who ask for less motion */
@media (prefers-reduced-motion:no-preference) {
  .brp-head { animation:brp-rise 0.5s ease-out both; }
  @keyframes brp-rise { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:none; } }
}
"""


def apply_theme():
    st.html(f"<style>{_token_css()}{_CSS}</style>")
