# Contributing

Thank you for improving the platform. It is used to teach, so clear code matters as much as working code.

## Before you start

1. Read [docs/COMPLIANCE.md](docs/COMPLIANCE.md). The one rule that is never negotiable: the platform explains, it never advises.
2. Read [docs/FRONTEND.md](docs/FRONTEND.md) if you are changing anything on screen.
3. Open an issue describing the change before a large pull request.

## Setting up

```bash
make install        # .venv, dependencies, and the pre-commit hooks
cp .env.example .env
make dev            # static site on :8000, research app on :8501
```

## How a change reaches production

1. Branch from `main` (`feature/...`, `fix/...`, `docs/...`). `main` is protected: nobody pushes to it directly.
2. Commit in small steps with messages that say what changed and why. The pre-commit hooks run Ruff, Bandit and Gitleaks before every commit.
3. Open a pull request using the template. Every pull request runs CI (tests on Python 3.10 and 3.12, lint, a site build), the security checks (pip-audit, Bandit, Gitleaks across the whole history, CodeQL, a production image build), and, from this repository, a deploy to the staging app with a full end-to-end check.
4. Merge when everything is green and the code owner has reviewed it. The merge deploys to production only after CI and the security checks pass again on `main`, followed by a smoke test.
5. Update CHANGELOG.md and, for scope changes, docs/WBS.md in the same pull request.

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
make check          # lint, tests, dependency audit, Bandit and the secret scan
make dev            # look at what you changed, in light and dark mode, at phone width
```

Add tests for new behaviour. If you add a risk check, add a test for each of its three results.
