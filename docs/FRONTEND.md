# Front-End Standard

The dashboard follows the ABC front-end standard (October 2026), adapted to Streamlit. That standard is a hybrid: the structure, layout, accessibility, motion and release rules of the WeThinkCode_ front-end standard, with the look of africasblockchainclub.com - dark first, one amber accent, Geist, glass cards, the ABC logo tile, the elephant mascot and the home video loop. This file records how each rule is met and where the platform deliberately differs, so a difference is a decision and not an accident.

## How the rules are met

| Rule | How |
|---|---|
| One centred column, equal sides | `[data-testid="stMainBlockContainer"]` capped at 76rem with `clamp(1rem, 4vw, 2.5rem)` sides (`dashboards/ui/theme.py`). Measured equal at 375, 390, 768, 1280, 1440 and 1920 pixels wide |
| Blocks fill the column | Cards, tiles, notices and report tables run the full column width |
| The page never moves sideways | `overflow-y: scroll` on `html`, `overflow-x: clip` on `body`; wide tables and the tab strip scroll inside themselves |
| Colour tokens, dark and light | ABC's palette as CSS variables (dark first; amber `#f99c00` on dark, `#b75000` on light so it passes AA as text), with dark values chosen from Streamlit's own theme setting (`st.context.theme`) and the operating system preference as the fallback. Streamlit's theme in `.streamlit/config.toml` uses the same values |
| Type tuned per mode | Geist, as on the ABC site; dark mode lifts the light weight one step |
| Contrast | Every text pairing comes from the standard's AA palette. Risk status is never shown by colour alone: each card carries a text label |
| Buttons | Pills at least 48 pixels tall; one accent colour for actions; disabled buttons say why ("Choose a token first") |
| Help text at least 15 pixels | Captions and widget labels set to 0.9375rem |
| Main actions above the fold | The home stage holds the headline, one line and both main actions at every width checked, over the muted video loop with the mascot beside it on wide screens |
| Motion | Sections fade and rise once; nothing loops; `prefers-reduced-motion` turns it off |
| Navigation follows the job | Home, Research a token, Reports, Attack cost, How it works |
| One view at a time | A report opens with summary tiles, then one tab per phase, opening on Risk checks |
| Errors stay on screen | Every failure shows what happened and what to do next, and is logged |
| Every dependency has an off switch | AI, payments, email, screenshots: see `config.py` and `.env.example` |
| Build stamp | `BUILD` in `config.py`, shown in the footer |
| Words | British English, no contractions, no long dashes, plain labels |

## Deliberate differences

1. **Two front ends.** The reading pages (home, blockchains, reports, method) are plain HTML built from the shell itself: `abc-shell.css` and the standard's own `wtc-shell.js`, unchanged, with the home stage, scroll-built tiles and reveal-once. Only live research and payments use Streamlit (below). See docs/adr/0002.
2. **Streamlit for the research app, not the shell page.** The standard's default stack is one plain HTML page built from `wtc-shell.css` and `wtc-shell.js`. Streamlit is kept for live research so the Python data pipeline and the payment flow stay in one language. The shell's tokens and component styles are carried over into it; its JavaScript behaviours run only on the static pages.
3. **Navigation in the app is Streamlit's top bar.** It holds the logo and the page links and is aligned to the content column. It is not the shell's sticky bar with a theme button: the theme follows Streamlit's settings menu and the operating system instead.
4. **Media.** The logo tile, mascot, still and home video live in `dashboards/static`. The site build copies them, and Caddy serves them with the right content types. (Streamlit's own static server sends `.mp4` as `text/plain`, which browsers refuse to play, which is one reason the home page is not a Streamlit page.)
5. **No access list.** The platform is a public teaching tool with no personal data, so it has no Access tab. If a fork adds accounts or stores personal data, it must add server-side access checks as the standard describes.
6. **The logo is the ABC tile.** `dashboards/static/abc-logo-tile.png` is the white ABC mark inside the standard's corner-cut tile on ABC black, readable on both themes. A fork without that file gets a tile drawn from its brand settings instead.

## Known gaps

- At 768 pixels wide, Streamlit's collapsed menu ignores the header offset, so the logo sits about 15 pixels left of the content edge.
- Streamlit decides the colours of some of its own widgets (the select box menu, the status box); they follow `.streamlit/config.toml` rather than the CSS tokens.

## Checking a change

```bash
streamlit run dashboards/app.py
```

Open the app at 390 and 1440 pixels wide in both themes. Check that the left and right space around the content is equal, that tables reach the right edge of the column, and that nothing scrolls sideways.
