# Deploying

Any host that runs a Python web service can run the platform. The steps below use Render as the example; check Render's own documentation for current plans and limits, because they change.

## Before you deploy

- `pytest` and `ruff check .` pass.
- You have decided which features to switch on. A public copy with no API key runs data-only reports, which cost nothing.
- **Storage.** Many hosts, including free tiers, wipe the local disk on every deploy or restart. Reports are saved to `reports/` and to the database, so on such a host set `DATABASE_URL` to a hosted Postgres database and expect the files in `reports/` to be lost on redeploy.
- **Screenshots.** Playwright needs a browser, which is heavy for a small host. Set `SCREENSHOTS_ENABLED=false` unless you install one in the build.

## Render

1. Push the repository to GitHub.
2. In Render, create a **Web Service** from the repository.
3. Use these settings:

   | Setting | Value |
   |---|---|
   | Environment | Python 3 |
   | Build command | `pip install -r requirements.txt` |
   | Start command | `streamlit run dashboards/app.py --server.port $PORT --server.address 0.0.0.0` |

4. Add environment variables from `.env.example` in the **Environment** tab. Never commit `.env`.
5. Deploy, then open the URL and check the footer: it shows the build number and whether AI and payments are on.

## Updating

Push to `main`. CI runs the tests and the linter; Render redeploys when the push lands. Bump `BUILD` in `config.py` with each release so the footer shows which build is live.

## If something goes wrong

- **The app does not start**: read the service logs. The usual cause is a missing system library for the PDF export; see the Quick start in the README.
- **AI write-ups are off**: the footer says so. Check `ANTHROPIC_API_KEY` and `AI_ENABLED`.
- **The payment demo shows a configuration error**: `REPORT_RECIPIENT_ADDRESS` is not set.
