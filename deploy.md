# Deploying

The live copy runs on Fly.io in Johannesburg: https://blockchain-research-platform.fly.dev

## Before you deploy

- `pytest` and `ruff check .` pass.
- You know which features are on. The live copy sets `AI_REQUIRES_PAYMENT=true` in `fly.toml`, so AI write-ups only ever run behind a payment, even if an API key is added first.

## Fly.io (the live copy)

`fly.toml`, `Dockerfile` and `scripts/start.sh` hold the whole setup:

- one `shared-cpu-1x` machine with 1 GB of memory in `jnb`, stopped when idle and started on the next visit;
- a 1 GB volume, `brp_data`, mounted at `/data`, holding the reports, the SQLite database and the usage log (`DATA_DIR=/data`);
- the sample reports in `reports/` are copied onto an empty volume on first boot;
- chart screenshots are off, because the image has no browser.

Because the volume belongs to one machine, the app runs on one machine. Move to Postgres (`DATABASE_URL`) and shared report storage before adding more.

### First-time setup (already done for the live copy)

```bash
fly apps create blockchain-research-platform --org personal
fly volumes create brp_data --region jnb --size 1 --app blockchain-research-platform
fly deploy --remote-only --ha=false
```

### Each release

Bump `BUILD` in `config.py`, push to `main` (CI runs the tests), then:

```bash
fly deploy --remote-only
```

The footer on the live site shows the build number, so you can confirm which build is serving.

### Switching on paid AI write-ups

AI write-ups cost 2 USDC on Base mainnet, paid to the business wallet. Secrets never go in `fly.toml` or in git:

```bash
fly secrets set --app blockchain-research-platform \
  ANTHROPIC_API_KEY=sk-ant-... \
  REPORT_RECIPIENT_ADDRESS=0xYourBusinessWallet \
  PAYMENTS_ENABLED=true
```

Setting secrets restarts the machine. Then make one real 2 USDC payment yourself, and check that the write-up arrives and that the payment row is recorded, before you announce the feature. Set a monthly spending limit in the Anthropic console as a backstop.

To switch paid write-ups off again: `fly secrets set PAYMENTS_ENABLED=false --app blockchain-research-platform`.

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
