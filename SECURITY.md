# Security Policy

The platform takes real stablecoin payments and holds an AI provider key, so security reports are welcome and handled first.

## Reporting a vulnerability

**Do not open a public issue.** Report privately through GitHub: **Security > Report a vulnerability** on this repository (a private security advisory). Include what you found, how to reproduce it, and what an attacker could do with it.

| Step | Target time |
|---|---|
| Acknowledgement | 3 working days |
| First assessment and severity | 7 working days |
| Fix for a critical or high issue | 14 days, or a documented mitigation sooner |

You will be credited in the advisory unless you ask not to be. Please give us a reasonable chance to fix an issue before you publish it.

## In scope

- The live site and app at https://blockchain-research-platform.fly.dev
- Everything in this repository, including the GitHub Actions workflows
- Payment verification (`payment_verifier.py`) and anything that could unlock a write-up without paying, pay the wrong wallet, or replay a payment
- Injection into reports or pages (cross-site scripting through report content), and reading files outside `reports/`
- Leaks of secrets, payer email addresses or payment records

## Out of scope

- The third-party services the platform reads (CoinGecko, DexScreener, public RPC endpoints, GitHub); report those to their owners
- `teaching/` and `x402/`: local teaching examples, never deployed
- Denial of service by volume, and findings that need a compromised device or browser extension
- Missing headers or settings with no demonstrated impact

## How the platform is protected

The threat model in [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) lists each asset, threat and control. In short:

- **Every pull request** runs the tests, Ruff, Bandit, pip-audit, a Gitleaks scan of the full history, CodeQL, a production image build, and a full end-to-end check against the staging app. `main` is protected: nothing merges unless those pass.
- **Supply chain:** Python packages, GitHub Actions (by commit) and base images (by digest) are pinned; Dependabot proposes updates weekly; pip-audit and CodeQL also run weekly on an unchanged codebase.
- **Secrets** live only in Fly and GitHub secrets, never in the repository; deploy tokens are scoped to one app.
- **Runtime:** the container runs as an unprivileged user; only Caddy is exposed; the site sends a strict content security policy and HSTS.
- **Money:** a payment must be recent, to the configured wallet, in an accepted stablecoin, for the full amount, and can unlock one write-up only. The live site refuses AI write-ups unless payments are on.

## Supported versions

Only the current `main` branch, which is what runs in production, receives security fixes.
