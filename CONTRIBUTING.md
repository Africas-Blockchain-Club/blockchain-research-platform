# Contributing

Thank you for improving the platform. It is used to teach, so clear code matters as much as working code.

## Before you start

1. Read [docs/COMPLIANCE.md](docs/COMPLIANCE.md). The one rule that is never negotiable: the platform explains, it never advises.
2. Read [docs/FRONTEND.md](docs/FRONTEND.md) if you are changing anything on screen.
3. Open an issue describing the change before a large pull request.

## Setting up

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Rules for code

- **One module per external service.** A new data source gets its own fetcher function; a new provider gets its own adapter. Nothing else imports the provider's library.
- **Every dependency has an off switch** in `config.py`, and the platform still works with it off.
- **Fail loudly.** A failure shows the user what happened and what to do next, and is logged. Never return an empty or partial result as if it were whole.
- **Missing data is "No data", never "Clear".**
- **Comments explain why, not what.**
- **Secrets live in `.env` only.** Never commit a key, and rotate any key that has been pasted anywhere public.

## Rules for words

British English, no contractions, no long dashes (use a hyphen or a semicolon), and plain words a first-time user would not need to ask about. Currency is shown in US Dollars with the Rand in brackets.

## Before you open a pull request

```bash
pytest
ruff check .
streamlit run dashboards/app.py   # look at what you changed, in light and dark mode, on a phone width
```

Add tests for new behaviour. If you add a risk check, add a test for each of its three results.
