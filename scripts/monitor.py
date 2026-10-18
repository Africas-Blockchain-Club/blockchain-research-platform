"""
End-to-end check of the live platform. Runs unattended from GitHub Actions
(.github/workflows/monitor.yml) and on demand from the brp-check skill.

  python scripts/monitor.py            quick: DNS, health endpoint, payment networks
  python scripts/monitor.py --full     also: every page in a real browser, and the
                                       data pipeline against the live data sources
  add --email                          email OWNER_ALERT_EMAIL when a check fails
  add --email-always                   email the result even when everything passes

Exit code 0 when every check passes, 1 otherwise, so a failure also shows up
as a failed workflow run (GitHub emails the repository owner about those too).
Nothing here pays, writes a report, or calls an AI model.
"""
import argparse
import os
import socket
import sys
import time
import traceback
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# The monitor only reads: never a model call, a payment or a browser screenshot
os.environ["AI_ENABLED"] = "false"
os.environ["SCREENSHOTS_ENABLED"] = "false"

import requests  # noqa: E402

SITE = os.getenv("MONITOR_URL", "https://blockchain-research-platform.fly.dev").rstrip("/")
# The networks the live site accepts; kept in step with fly.toml
LIVE_CHAINS = os.getenv("MONITOR_PAYMENT_CHAINS", "8453,42161,10,137,56,1")


def check_dns():
    host = urlparse(SITE).hostname
    addresses = sorted({info[4][0] for info in socket.getaddrinfo(host, 443)})
    return f"{host} resolves to {', '.join(addresses)}"


def check_health():
    last_error = None
    for attempt in range(3):
        try:
            resp = requests.get(f"{SITE}/_stcore/health", timeout=20)
            if resp.status_code == 200 and resp.text.strip() == "ok":
                return f"health endpoint answered ok in {resp.elapsed.total_seconds():.1f}s"
            last_error = f"status {resp.status_code}: {resp.text[:80]}"
        except requests.RequestException as e:
            last_error = str(e)
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"health endpoint failing after 3 tries: {last_error}")


def check_payment_networks():
    import payment_verifier as pv

    results, problems = [], []
    for chain_id in [int(c) for c in LIVE_CHAINS.split(",")]:
        network = pv.NETWORKS[chain_id]
        try:
            got = int(pv._rpc_call(chain_id, "eth_chainId", []), 16)
            if got != chain_id:
                problems.append(f"{network['name']}: RPC reports chain {got}")
                continue
            for symbol, (contract, decimals) in network["tokens"].items():
                raw = pv._rpc_call(chain_id, "eth_call", [{"to": contract, "data": "0x313ce567"}, "latest"])
                if int(raw, 16) != decimals:
                    problems.append(f"{symbol} on {network['name']}: decimals {int(raw, 16)}, expected {decimals}")
            results.append(network["name"])
        except Exception as e:
            problems.append(f"{network['name']}: {e}")
    if problems:
        raise RuntimeError("; ".join(problems))
    return f"RPC and token contracts answer correctly on {', '.join(results)}"


def check_pages():
    from playwright.sync_api import sync_playwright

    pages = [
        ("/", "Learn to read a token"),
        ("/research", "Research a token"),
        ("/reports", "Research reports"),
        ("/attack-cost", "What does it cost to attack Ethereum?"),
        ("/how-it-works", "Research, not advice"),
    ]
    footer = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.getenv("MONITOR_CHROMIUM") or None)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        for path, heading in pages:
            page.goto(SITE + path, timeout=60000)
            page.get_by_text(heading, exact=False).first.wait_for(timeout=60000)
            crashed = page.locator('[data-testid="stException"]')
            if crashed.count():
                raise RuntimeError(f"{path} shows an error: {crashed.first.inner_text()[:200]}")
        page.goto(SITE + "/reports", timeout=60000)
        page.get_by_text("Research reports").first.wait_for(timeout=60000)
        reports = page.locator("a.brp-link")
        if reports.count():
            page.goto(SITE + "/" + reports.first.get_attribute("href"), timeout=60000)
            page.get_by_role("tab", name="Risk checks").wait_for(timeout=60000)
        footer = page.locator(".brp-footer").last.inner_text()
        browser.close()
    if errors:
        raise RuntimeError(f"browser errors: {errors[:3]}")
    status_line = next((line for line in footer.splitlines() if line.strip().startswith("Build")), "build unknown")
    status = " · ".join(part.strip() for part in status_line.split("·")[:3])
    return f"{len(pages)} pages and a report render with no errors ({status})"


def check_pipeline():
    from data_analytics.data_report import build_data_report
    from data_science.compliance import assert_educational
    from tools.report_generator import fetch_and_analyse

    analysis = fetch_and_analyse("ETH", log_fn=lambda _msg: None)
    info = analysis["data_summary"]["token_info"]
    if "contract address" not in str(info.get("dex_pair_match")):
        raise RuntimeError(f"ETH pool was not found by contract address: {info.get('dex_pair_match')}")
    if not info.get("market_cap_usd"):
        raise RuntimeError("CoinGecko returned no market cap for ETH")
    if len(analysis["risk_checks"]) != 10:
        raise RuntimeError(f"expected 10 risk checks, got {len(analysis['risk_checks'])}")
    assert_educational(build_data_report("ETH", analysis["data_summary"], "monitor run"))
    return f"ETH data fetched (main pool {info.get('dex')} on {info.get('chain')}); report passes the advice check"


def run(full):
    checks = [("DNS", check_dns), ("Site health", check_health), ("Payment networks", check_payment_networks)]
    if full:
        checks += [("Pages in a browser", check_pages), ("Data pipeline", check_pipeline)]
    results = []
    for name, check in checks:
        try:
            results.append((name, True, check()))
        except Exception as e:
            detail = f"{e}\n{traceback.format_exc(limit=2)}" if os.getenv("MONITOR_DEBUG") else str(e)
            results.append((name, False, detail))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--email", action="store_true", help="email the owner when a check fails")
    parser.add_argument("--email-always", action="store_true", help="email the result even when all pass")
    args = parser.parse_args()

    results = run(args.full)
    failed = [r for r in results if not r[1]]
    lines = [f"{'PASS' if ok else 'FAIL'}  {name}: {detail}" for name, ok, detail in results]
    report = f"Monitor run against {SITE} ({'full' if args.full else 'quick'})\n\n" + "\n".join(lines)
    print(report)

    if (args.email and failed) or args.email_always:
        import emailer

        subject = (f"{len(failed)} check(s) failing on the live site" if failed
                   else "All checks passed on the live site")
        run_url = os.getenv("GITHUB_RUN_URL", "")
        body = report + (f"\n\nWorkflow run: {run_url}" if run_url else "")
        body += "\n\nFirst steps: fly status --app blockchain-research-platform; fly logs --app blockchain-research-platform"
        if not emailer.alert_owner(subject, body):
            print("Could not send the email: OWNER_ALERT_EMAIL or SMTP settings are missing or wrong.")
            return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
