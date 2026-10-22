"""
Decide whether a pip-audit result passes, allowing only advisories that have been
reviewed and accepted. Reads `pip-audit -f json` on standard input.

Accepted until REVIEW_BY (issue #16): advisories in Pillow 12.3.0 whose only fix
is Pillow 13 or later. Pillow arrives through Streamlit, which (up to 1.66.0)
requires pillow<13, so the fix cannot be installed yet. The advisories are
triggered by opening crafted image, PDF or font files, and the platform never
opens an image it did not ship. Any other advisory fails the check, and after
REVIEW_BY this exception fails too, so it is looked at again rather than left.

  pip-audit -r requirements.txt -f json --progress-spinner off | python scripts/audit_gate.py
"""
import datetime
import json
import sys

REVIEW_BY = datetime.date(2026, 10, 29)
ACCEPTED_PACKAGE, ACCEPTED_VERSION = "pillow", "12.3.0"


def _major(version):
    try:
        return int(version.split(".")[0])
    except (ValueError, IndexError):
        return 0


def judge(report, today):
    """Returns (accepted, failing): lists of "package version id" strings."""
    accepted, failing = [], []
    for dep in report.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            line = f"{dep['name']} {dep['version']} {vuln['id']} (fixed in {', '.join(vuln['fix_versions']) or 'none'})"
            fixes = vuln.get("fix_versions") or []
            known = (dep["name"].lower() == ACCEPTED_PACKAGE and dep["version"] == ACCEPTED_VERSION
                     and fixes and all(_major(v) >= 13 for v in fixes))
            (accepted if known and today <= REVIEW_BY else failing).append(line)
    return accepted, failing


def main():
    accepted, failing = judge(json.load(sys.stdin), datetime.date.today())
    for line in accepted:
        print(f"accepted until {REVIEW_BY} (issue #16): {line}")
    for line in failing:
        print(f"FAILING: {line}")
    if failing:
        sys.exit(1)
    print("Dependency audit passed" + (f", with {len(accepted)} accepted advisories" if accepted else ""))


if __name__ == "__main__":
    main()
