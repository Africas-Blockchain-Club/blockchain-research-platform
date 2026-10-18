## What and why

<!-- What this changes, and the reason. Link the issue or WBS element (docs/WBS.md). -->

## How it was checked

- [ ] `make check` passes (lint, tests, dependency audit, Bandit, secret scan)
- [ ] New behaviour has tests; a new risk check has a test for each of its three results
- [ ] Screens changed: checked at 390 and 1440 pixels wide, in light and dark mode
- [ ] Staging deploy and its end-to-end check are green

## Risk

- [ ] Touches payments, secrets, the Caddyfile, the Dockerfile or a workflow: the threat model (docs/THREAT_MODEL.md) is still true, or is updated here
- [ ] Changes anything a reader sees: it explains and never advises (docs/COMPLIANCE.md)
- [ ] CHANGELOG.md updated
