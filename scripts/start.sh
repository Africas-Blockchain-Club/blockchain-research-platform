#!/bin/sh
# Container start. Three processes, each unprivileged:
#   Caddy      serves the static site and proxies /app (the only public port)
#   Streamlit  the research app, on localhost only
#   refresher  updates the featured blockchains' network data every 15 minutes
# If Caddy or Streamlit stops, the health check fails and Fly restarts the machine.
set -eu
DATA_DIR="${DATA_DIR:-/data}"

mkdir -p "$DATA_DIR/reports"
# Seed the bundled sample reports onto an empty volume, once
if [ -z "$(ls -A "$DATA_DIR/reports" 2>/dev/null)" ] && [ -d /app/reports ]; then
  cp /app/reports/*_research_report.* "$DATA_DIR/reports/" 2>/dev/null || true
fi

# A fresh volume is owned by root; everything below runs as the app user
if [ "$(id -u)" = "0" ]; then
  chown -R app:app "$DATA_DIR"
  AS_APP="setpriv --reuid=app --regid=app --init-groups env HOME=/home/app"
else
  AS_APP=""
fi

# Build the site before Caddy starts, so the first request is never a 404
$AS_APP python -m sitegen.build || echo "Initial site build failed; the refresher will retry" >&2

$AS_APP python scripts/refresh_networks.py --loop &
$AS_APP streamlit run dashboards/app.py &
exec $AS_APP caddy run --config /app/Caddyfile --adapter caddyfile
