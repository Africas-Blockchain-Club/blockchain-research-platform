# 0001: The platform explains and never advises

**Status:** Accepted, 18 October 2026

## Context
Version 2 gave tokens a 0 to 100 score, a Buy to Sell verdict, entry and exit triggers and a brief tailored to the reader. In South Africa crypto assets are financial products under the FAIS Act, and a recommendation needs an authorised provider. The platform is used to teach, and will be forked by students.

## Decision
Remove every rating, verdict, trigger and tailored output. Replace the score with rule-based risk checks (flagged, clear or no data, never summed). Enforce it in code: an advice-language check on every report, and a disclaimer written by code rather than the model.

## Options considered
- **Keep the score with a disclaimer.** Rejected: any single number reads as a rating.
- **Rename the score.** Rejected for the same reason.

## Consequences
Reports teach instead of judge. The check can reject a legitimate sentence; when it does, the pattern is narrowed and the sentence added to the tests, never the pattern deleted. See docs/COMPLIANCE.md.
