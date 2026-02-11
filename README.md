# Research Team Folder – Africa’s Blockchain Club

This folder is the single source of truth for all research blueprints, forensic reports, dashboards, and tools.

## Folder Structure & Rules (Strict – Follow for Scalability)

- **`blueprints/`**  
  All repeatable methodologies live here.  
  Naming convention: `task-name-blueprint-v1.0.md` (lowercase, hyphens)  
  Examples:  
  - `token-analysis-blueprint-v1.0.md` ← current (token forensic audits)  
  - Next: `defi-yield-blueprint-v1.0.md`, `nft-valuation-blueprint-v1.0.md`, etc.  
  → When adding a new task, create a new .md file here with the above naming.

- **`reports/`**  
  Output forensic reports from applying blueprints.  
  Sub-folders per task: `reports/token-analysis/`, `reports/defi-yield/`, etc.  
  Files: Markdown only (PDFs generated live from dashboard — no static PDFs in repo).

- **`dashboards/`**  
  Live Streamlit app (`app.py`). Automatically reads all blueprints & reports.  
  → When new blueprint/report added, update the sidebar/selectors here.

- **`data_engineering/`**, **`data_science/`**, **`data_analytics/`**  
  Pipelines, notebooks, metrics — grow as needed per task.

- **`tools/`**  
  Shared utilities (PDF generator, etc.).

## How to Add a New Task/Blueprint (Future-Proof Process)

1. Create new file in `blueprints/` → `new-task-blueprint-v1.0.md`
2. Add outline/content following the token-analysis style
3. (Optional) Create sub-folder in `reports/` → `reports/new-task/`
4. Update `dashboards/app.py` to include the new blueprint in sidebar/tabs
5. Commit with clear message: "Add new-task blueprint"

This keeps everything organized and scalable as the team grows.

**Current Active Blueprint**: Token Analysis v1.0 (liquidity-first forensic audits)

Maintained by Peter Manda & Africa’s Blockchain Club Research Team — Feb 2026