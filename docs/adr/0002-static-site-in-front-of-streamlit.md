# 0002: A static site in front of the Streamlit research app

**Status:** Accepted, 19 October 2026

## Context
Streamlit ships a large JavaScript application and opens a live connection before it shows anything, so every page loaded noticeably slower than a normal website. Most visitors only read: the home page, the blockchain profiles and the reports.

## Decision
Generate the reading pages as plain HTML (sitegen/, Jinja2, the ABC front-end shell) and serve them from Caddy. Keep Streamlit only for live research and payments, under /app on the same host. Rebuild the site at start-up, after each saved report and after each network-data refresh.

## Options considered
- **Rewrite as FastAPI and HTML.** Fastest everywhere, but rebuilds the wallet, payment and research screens; deferred.
- **Optimise Streamlit only.** Cannot remove its start-up cost.

## Consequences
Reading pages load in tens of milliseconds and can carry a strict content security policy. There are now two front ends sharing one set of design tokens; the monitor checks both run the same build.
