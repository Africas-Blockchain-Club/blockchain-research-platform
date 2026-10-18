# 0004: One Fly.io machine with a volume and SQLite

**Status:** Accepted, 18 October 2026

## Context
The platform needs somewhere persistent for reports and payment records, close to South African users, at low cost.

## Decision
One always-on machine in Johannesburg (jnb) with a 1 GB volume holding the reports, the SQLite database and the generated site. Daily volume snapshots. A separate staging app without a volume receives every pull request first.

## Options considered
- **Fly Postgres.** More robust and allows several machines, at a higher cost and with more to operate.

## Consequences
Simple and cheap; a machine restart is a short outage. Moving to Postgres is a configuration change (DATABASE_URL), but the report files and the site would also need shared storage before adding machines.
