# Deploying

The live copy runs on Fly.io in Johannesburg: https://blockchain-research-platform.fly.dev

## Before you deploy

- `pytest` and `ruff check .` pass.
- You know which features are on. The live copy sets `AI_REQUIRES_PAYMENT=true` in `fly.toml`, so AI write-ups only ever run behind a payment, even if an API key is added first.

## Fly.io (the live copy)

`fly.toml`, `Dockerfile` and `scripts/start.sh` hold the whole setup:

- one `shared-cpu-1x` machine with 1 GB of memory in `jnb`, always running (`min_machines_running = 1`, like wtc-codequest), so there is no cold start;
- a 1 GB volume, `brp_data`, mounted at `/data`, holding the reports, the SQLite database and the usage log (`DATA_DIR=/data`);
- the sample reports in `reports/` are copied onto an empty volume on first boot;
- Caddy in front of Streamlit (see below);
- chart screenshots are off, because the image has no browser.

Because the volume belongs to one machine, the app runs on one machine. Move to Postgres (`DATABASE_URL`) and shared report storage before adding more.

### First-time setup (already done for the live copy)

```bash
fly apps create blockchain-research-platform --org personal
fly volumes create brp_data --region jnb --size 1 --app blockchain-research-platform
fly deploy --remote-only --ha=false
```

### Each release: the pipeline, not a laptop

Releases go through GitHub, never `fly deploy` from a laptop:

1. A pull request deploys to **staging** (`blockchain-research-platform-staging`, `fly.staging.toml`: no volume, no payments, no AI key, stops when idle) and runs the full end-to-end monitor against it.
2. Merging to `main` runs CI and the security checks again on the merged commit; only then does `deploy.yml` deploy to production, followed by a smoke test against the live site.
3. Bump `BUILD` in `config.py` and add a CHANGELOG.md entry in the pull request, so the footer shows which build is live.

The workflows authenticate with deploy tokens scoped to one app each, stored as GitHub secrets (`FLY_API_TOKEN` for production, `FLY_API_TOKEN_STAGING` for staging). To rotate one:

```bash
fly tokens create deploy --app blockchain-research-platform --expiry 8760h | gh secret set FLY_API_TOKEN --repo Africas-Blockchain-Club/blockchain-research-platform
```

In an emergency, an administrator can still deploy by hand with `fly deploy --remote-only`; record why in the changelog.

### How the machine runs

`scripts/start.sh` starts three processes as the unprivileged `app` user: Caddy on port 8080 (the only public port: the static site, the `/app` proxy and the security headers), Streamlit on localhost, and the network refresher, which updates the seven blockchains' data and rebuilds the site every 15 minutes. Fly's health check goes through Caddy to Streamlit, so it fails, and Fly restarts the machine, if either stops.

### Paid AI write-ups

An AI write-up costs 2 US Dollars, paid in USDC or USDT on Base, Arbitrum, Optimism, Polygon, BNB Chain or Ethereum (`PAYMENT_CHAINS` in `fly.toml`). The payer connects a wallet; the page checks which of those coins they hold, preselects one they can afford, switches the wallet to that network and sends the transfer. Payments go to the business wallet in the `REPORT_RECIPIENT_ADDRESS` secret.

Secrets never go in `fly.toml` or in git:

```bash
fly secrets set --app blockchain-research-platform \
  ANTHROPIC_API_KEY=sk-ant-... \
  REPORT_RECIPIENT_ADDRESS=0x... \
  PAYMENTS_ENABLED=true
```

To switch paid write-ups off again: `fly secrets set PAYMENTS_ENABLED=false --app blockchain-research-platform`.

### Alerts: payments and failures

The app emails `OWNER_ALERT_EMAIL` when a payment is confirmed (so the Anthropic credit can be topped up) and when a paid write-up fails. It needs the SMTP settings as secrets too. From the folder that holds your `.env`:

```bash
grep -E '^(SMTP_HOST|SMTP_PORT|SMTP_USER|SMTP_PASSWORD)=' .env | xargs fly secrets set --app blockchain-research-platform
fly secrets set OWNER_ALERT_EMAIL=you@example.com --app blockchain-research-platform
```

### The monitor

`.github/workflows/monitor.yml` runs `scripts/monitor.py` on GitHub's machines: a quick check every 30 minutes, a full check (every page in a browser, and the data pipeline) every day at 06:00 South African time, and a full report by email every Monday at 07:00. A failure emails `OWNER_ALERT_EMAIL` and fails the run, which GitHub also emails to the repository owner. The workflow needs the same mail settings as repository secrets:

```bash
grep -E '^(SMTP_HOST|SMTP_PORT|SMTP_USER|SMTP_PASSWORD)=' .env | while IFS='=' read -r key value; do
  gh secret set "$key" --body "$value" --repo Africas-Blockchain-Club/blockchain-research-platform
done
gh secret set OWNER_ALERT_EMAIL --body you@example.com --repo Africas-Blockchain-Club/blockchain-research-platform
```

GitHub pauses scheduled workflows in a repository with no activity for 60 days; `gh workflow enable monitor.yml` turns it back on. Run `scripts/monitor.py --full` locally at any time, and `scripts/payments_report.py` on the machine to list payments and whether each received its write-up.

### Useful commands

```bash
fly logs --app blockchain-research-platform
fly ssh console --app blockchain-research-platform -C "ls /data/reports"
fly volumes snapshots list brp_data --app blockchain-research-platform
```

Fly takes daily snapshots of the volume and keeps 5 days of them.

## Other hosts

Any host that runs a Docker image or a Python web service can run the platform:

- Start command: `streamlit run dashboards/app.py --server.port $PORT --server.address 0.0.0.0`.
- Point `DATA_DIR` at persistent storage, or use `DATABASE_URL` with Postgres. Many free tiers wipe the disk on every deploy, which deletes saved reports.
- Set `SCREENSHOTS_ENABLED=false` unless the host has a browser for Playwright.

## If something goes wrong

- **The app does not start**: run `fly logs`. A failed health check in the first seconds after boot is normal while Streamlit starts.
- **AI write-ups say "Not available yet"**: payments are off on a deployment that requires them. That is the safety switch working.
- **The payment screen shows a configuration error**: `REPORT_RECIPIENT_ADDRESS` is not set.
