# 0006: One adapter and an off switch for every external dependency

**Status:** Accepted, 18 October 2026

## Context
The platform depends on an AI provider, several data APIs, public RPC nodes, GitHub, SMTP, a browser for screenshots and a host. Any of them can fail, change or disappear.

## Decision
Each dependency sits behind one module (data_science/llm.py, data_engineering/*.py, payment_verifier.py, emailer.py, db.py), configured from config.py, with a defined off state. A failure becomes a labelled "No data" or a clear error, never a quiet wrong answer. The AI is optional: the data-only report is the platform working with AI switched off.

## Consequences
Swapping a provider touches one file. Tests run fully offline. The cost is a little more structure than a script would need.
