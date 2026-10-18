# Front-End Standard

The dashboard follows the WeThinkCode_ front-end standard (September 2026), adapted to Streamlit. This file records how each rule is met and where the platform deliberately differs, so a difference is a decision and not an accident.

## How the rules are met

| Rule | How |
|---|---|
| One centred column, equal sides | `[data-testid="stMainBlockContainer"]` capped at 76rem with `clamp(1rem, 4vw, 2.5rem)` sides (`dashboards/ui/theme.py`). Measured equal at 375, 390, 768, 1280, 1440 and 1920 pixels wide |
| Blocks fill the column | Cards, tiles, notices and report tables run the full column width |
| The page never moves sideways | `overflow-y: scroll` on `html`, `overflow-x: clip` on `body`; wide tables and the tab strip scroll inside themselves |
| Colour tokens, light and dark | The standard's palette as CSS variables, with dark values chosen from Streamlit's own theme setting (`st.context.theme`) and the operating system preference as the fallback. Streamlit's theme in `.streamlit/config.toml` uses the same values |
| Type tuned per mode | Figtree; dark mode lifts the light weight one step and eases the display weight |
| Contrast | Every text pairing comes from the standard's AA palette. Risk status is never shown by colour alone: each card carries a text label |
| Buttons | Pills at least 48 pixels tall; one accent colour for actions; disabled buttons say why ("Choose a token first") |
| Help text at least 15 pixels | Captions and widget labels set to 0.9375rem |
| Main actions above the fold | The home band holds the headline, one line and both main actions at every width checked |
| Motion | Sections fade and rise once; nothing loops; `prefers-reduced-motion` turns it off |
| Navigation follows the job | Home, Research a token, Reports, Attack cost, How it works |
| One view at a time | A report opens with summary tiles, then one tab per phase, opening on Risk checks |
| Errors stay on screen | Every failure shows what happened and what to do next, and is logged |
| Every dependency has an off switch | AI, payments, email, screenshots: see `config.py` and `.env.example` |
| Build stamp | `BUILD` in `config.py`, shown in the footer |
| Words | British English, no contractions, no long dashes, plain labels |

## Deliberate differences

1. **Streamlit, not the shell page.** The standard's default stack is one plain HTML page built from `wtc-shell.css` and `wtc-shell.js`. This platform keeps Streamlit so that a student can fork it and run it with one command, and so the Python data pipeline stays in one language. The shell's tokens and component styles are carried over; its JavaScript behaviours are not.
2. **Navigation is Streamlit's top bar.** It holds the logo and the page links and is aligned to the content column. It is not the shell's sticky bar with a theme button: the theme follows Streamlit's settings menu and the operating system instead.
3. **No photographs.** The standard puts photos from the WeThinkCode_ media folder on the home screen and inner screens. This platform's brand is set in configuration so that any fork can rebrand it, and a fork has no photo library, so the home screen uses the brand band, which is the standard's own fallback when no photo loads.
4. **No access list.** The platform is a public teaching tool with no personal data, so it has no Access tab. If a fork adds accounts or stores personal data, it must add server-side access checks as the standard describes.
5. **The logo is drawn from configuration.** `dashboards/app.py` draws the brand initials on the accent colour, inside the standard's corner-cut tile shape, so there is no image file with a white edge to check.

## Known gaps

- At 768 pixels wide, Streamlit's collapsed menu ignores the header offset, so the logo sits about 15 pixels left of the content edge.
- Streamlit decides the colours of some of its own widgets (the select box menu, the status box); they follow `.streamlit/config.toml` rather than the CSS tokens.

## Checking a change

```bash
streamlit run dashboards/app.py
```

Open the app at 390 and 1440 pixels wide in both themes. Check that the left and right space around the content is equal, that tables reach the right edge of the column, and that nothing scrolls sideways.
