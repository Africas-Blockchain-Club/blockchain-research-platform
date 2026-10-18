#!/bin/sh
# Container start: make sure the data folder exists and is writable, seed the
# bundled sample reports on first boot, then run the app as the app user.
set -e
DATA_DIR="${DATA_DIR:-/data}"
mkdir -p "$DATA_DIR/reports"
if [ -z "$(ls -A "$DATA_DIR/reports" 2>/dev/null)" ] && [ -d /app/reports ]; then
  cp /app/reports/*_research_report.* "$DATA_DIR/reports/" 2>/dev/null || true
fi
# A fresh Fly volume is owned by root; the app runs unprivileged
if [ "$(id -u)" = "0" ]; then
  chown -R app:app "$DATA_DIR"
  exec su app -s /bin/sh -c "streamlit run dashboards/app.py"
fi
exec streamlit run dashboards/app.py
