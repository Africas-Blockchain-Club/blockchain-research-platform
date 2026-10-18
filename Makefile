# Everyday commands. Each one is what CI or the deploy pipeline runs.
.PHONY: help install lint test security check site dev refresh deploy-staging

help:            ## List the commands
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

install:         ## Create .venv and install everything, including the git hooks
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/pre-commit install

lint:            ## Ruff
	.venv/bin/ruff check .

test:            ## The offline test suite
	.venv/bin/pytest

security:        ## Dependency audit, Bandit and the secret scan, as in CI
	.venv/bin/pip-audit -r requirements.txt --progress-spinner off
	.venv/bin/bandit -q -r . -x ./.venv,./tests,./teaching,./site -ll
	.venv/bin/pre-commit run gitleaks --all-files

check: lint test security  ## Everything a pull request must pass

site:            ## Build the static site into ./site
	.venv/bin/python -m sitegen.build

refresh:         ## Refresh the featured blockchains' network data and rebuild the site
	.venv/bin/python scripts/refresh_networks.py

dev: site        ## Static site on :8000 and the research app on :8501, linked to each other
	SITE_URL=http://localhost:8000 APP_URL=http://localhost:8501 .venv/bin/streamlit run dashboards/app.py & \
	.venv/bin/python -m http.server 8000 -d site

deploy-staging:  ## Deploy this checkout to the staging app
	flyctl deploy --remote-only --config fly.staging.toml
