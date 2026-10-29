"""
End-to-end check of the live platform. Runs unattended from GitHub Actions
(.github/workflows/monitor.yml) and on demand from the brp-check skill.

  python scripts/monitor.py            quick: DNS, health endpoint, payment networks
  python scripts/monitor.py --full     also: every page in a real browser, the paying steps
                                       up to the wallet (never paying), the data pipeline,
                                       and the sources status the server publishes
  add --email                          email OWNER_ALERT_EMAIL when a check fails
  add --email-always                   email the result even when everything passes

Exit code 0 when every check passes, 1 otherwise, so a failure also shows up
as a failed workflow run (GitHub emails the repository owner about those too).
Nothing here pays, writes a report, or calls an AI model.
"""
import argparse
import os
import re
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
# The wallet every payment must go to. Staging takes no payments, so it sets
# MONITOR_EXPECT_PAYMENTS=false and only the fetch part of the paying check runs.
EXPECTED_RECIPIENT = os.getenv("MONITOR_RECIPIENT", "0x95CD2382EB8DF97fC1e0f3adAA1A9a97FB2b9431").lower()
EXPECT_PAYMENTS = os.getenv("MONITOR_EXPECT_PAYMENTS", "true").lower() == "true"

# A pretend browser wallet for the paying check. It answers like MetaMask with a
# zero balance account and refuses every transaction, so nothing is ever sent.
TEST_WALLET = """
window.__monitor = {sent: null};
window.ethereum = {isMetaMask: true, request: async ({method, params}) => {
  if (method === "eth_requestAccounts" || method === "eth_accounts") return ["0x000000000000000000000000000000000000dEaD"];
  if (method === "eth_chainId") return "0x2105";
  if (method === "wallet_switchEthereumChain") return null;
  if (method === "eth_sendTransaction") {
    window.__monitor.sent = params[0];
    throw {code: 4001, message: "refused by the monitor's test wallet"};
  }
  throw {code: 4200, message: "not supported by the monitor's test wallet"};
}};
"""


def check_dns():
    host = urlparse(SITE).hostname
    addresses = sorted({info[4][0] for info in socket.getaddrinfo(host, 443)})
    return f"{host} resolves to {', '.join(addresses)}"


def check_health():
    last_error = None
    for attempt in range(3):
        try:
            resp = requests.get(f"{SITE}/app/_stcore/health", timeout=20)
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

    # The static site, then the research app behind /app
    pages = [
        ("/", "Learn to"),
        ("/blockchains/", "Seven blockchains to learn from"),
        ("/blockchains/bitcoin.html", "The network right now"),
        ("/reports/", "Research reports"),
        ("/how-it-works.html", "Research, not advice"),
        ("/app/", "Research a blockchain"),
        ("/app/attack-cost", "What does it take to attack a blockchain?"),
    ]
    footer = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.getenv("MONITOR_CHROMIUM") or None)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        for path, heading in pages:
            page.goto(SITE + path, timeout=60000)
            try:
                page.get_by_text(heading, exact=False).first.wait_for(timeout=60000)
            except Exception:
                # One retry: a machine that has just started (staging stops when idle)
                # can be slow once; a second miss is a real failure
                page.goto(SITE + path, timeout=60000)
                try:
                    page.get_by_text(heading, exact=False).first.wait_for(timeout=60000)
                except Exception as e:
                    raise RuntimeError(f"{path} never showed {heading!r}: {type(e).__name__}") from e
            if page.get_by_text("Page not found").count() and path.startswith("/app"):
                raise RuntimeError(f"{path} shows Streamlit's 'Page not found' dialog")
            crashed = page.locator('[data-testid="stException"]')
            if crashed.count():
                raise RuntimeError(f"{path} shows an error: {crashed.first.inner_text()[:200]}")
        page.goto(SITE + "/reports/", timeout=60000)
        reports = page.locator("a.chain-card")
        if reports.count():
            page.goto(SITE + reports.first.get_attribute("href"), timeout=60000)
            page.get_by_text("Risk checks").first.wait_for(timeout=60000)
        page.goto(SITE + "/", timeout=60000)
        site_footer = page.locator("footer.site").inner_text()
        page.goto(SITE + "/app/", timeout=60000)
        page.get_by_text("Research a blockchain").first.wait_for(timeout=60000)
        footer = page.locator(".brp-footer").last.inner_text()
        site_build = re.search(r"Build (\S+)", site_footer)
        app_build = re.search(r"Build (\S+)", footer)
        if not site_build or not app_build or site_build.group(1) != app_build.group(1):
            raise RuntimeError(f"the site and the app run different builds ({site_build and site_build.group(1)}, "
                               f"{app_build and app_build.group(1)})")
        csp = page.request.get(SITE + "/").headers.get("content-security-policy", "")
        if "script-src 'self'" not in csp:
            raise RuntimeError("the static site is missing its content security policy")
        browser.close()
    if errors:
        raise RuntimeError(f"browser errors: {errors[:3]}")
    status_line = next((line for line in footer.splitlines() if line.strip().startswith("Build")), "build unknown")
    status = " · ".join(part.strip() for part in status_line.split("·")[:3])
    return f"{len(pages)} pages and a report render with no errors, security headers present ({status})"


def _wait_for_fetch(page, token):
    """After a fetch button press on a fresh visit: the data is ready, or raise with the page's error."""
    result = page.get_by_text(re.compile(rf"Data for .*{token}.* is ready|Could not fetch data|Please wait"))
    result.first.wait_for(timeout=120000)
    page.locator('[data-testid="stStatusWidget"]').wait_for(state="hidden", timeout=120000)
    failed = page.get_by_text(re.compile("Could not fetch data|Please wait a"))
    if failed.count():
        error = page.locator('[data-testid="stAlertContentError"], [data-testid="stAlert"]')
        detail = error.first.inner_text()[:200] if error.count() else failed.first.inner_text()
        raise RuntimeError(f"fetching {token} failed: {detail}")


def check_paying():
    """What a payer does, in a real browser: fetch a coin twice (the second comes
    from the shared cache), ask for the write-up, give an email, connect a wallet
    and press Pay. The test wallet refuses the transaction, so nothing is paid;
    the check reads where the transfer would have gone."""
    from playwright.sync_api import sync_playwright

    import payment_verifier as pv

    token = "ETH"
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.getenv("MONITOR_CHROMIUM") or None)
        # The research page does not count the monitor's fetches as searches
        agent = browser.new_page().evaluate("navigator.userAgent") + " BRP-monitor"
        context = browser.new_context(viewport={"width": 1280, "height": 900}, user_agent=agent)
        context.add_init_script(TEST_WALLET)
        page = context.new_page()

        def press(button):
            # A fresh visit each time: no box from an earlier press is left to misread
            page.goto(f"{SITE}/app/?token={token}", timeout=60000)
            page.get_by_text("Research a blockchain").first.wait_for(timeout=60000)
            page.get_by_role("button", name=button).first.click(timeout=60000)
            _wait_for_fetch(page, token)

        press("Fetch the free data")
        press("Fetch the free data")
        if not EXPECT_PAYMENTS:
            browser.close()
            return f"{token} fetched twice, the second from the shared cache (payments not expected here)"

        press("Get the AI write-up")
        email = page.get_by_role("textbox", name="Your email address")
        email.wait_for(timeout=60000)
        email.fill("monitor@example.com")
        email.press("Enter")
        frame_el = page.locator('iframe[src*="wallet_pay"]').first
        frame_el.wait_for(timeout=60000)
        frame = frame_el.content_frame
        connect = frame.locator("#connect")
        connect.wait_for(timeout=60000)
        frame.locator("#connect:not([disabled])").wait_for(timeout=60000)
        connect.click()
        pay = frame.locator("#pay")
        pay.wait_for(state="visible", timeout=90000)
        frame.locator("#pay:not([disabled])").wait_for(timeout=30000)
        options = frame.locator("#options label").count()
        pay.click()
        frame.locator("#status", has_text="monitor's test wallet").wait_for(timeout=30000)
        sent = frame_el.element_handle().content_frame().evaluate("window.__monitor.sent")
        browser.close()

    contracts = {contract.lower(): (n["name"], symbol, decimals) for n in pv.NETWORKS.values()
                 for symbol, (contract, decimals) in n["tokens"].items()}
    if not sent or not sent.get("data", "").startswith("0xa9059cbb"):
        raise RuntimeError(f"the Pay button did not prepare a stablecoin transfer: {sent}")
    if (sent.get("to") or "").lower() not in contracts:
        raise RuntimeError(f"the Pay button would send to {sent.get('to')}, which is not an accepted stablecoin")
    network, symbol, decimals = contracts[sent["to"].lower()]
    recipient = "0x" + sent["data"][10:74][-40:]
    amount = int(sent["data"][74:138], 16) / 10 ** decimals
    if recipient.lower() != EXPECTED_RECIPIENT:
        raise RuntimeError(f"payments would go to {recipient}, not the owner's wallet {EXPECTED_RECIPIENT}")
    return (f"{token} fetched twice, write-up step reached, wallet offered {options} ways to pay; Pay prepares "
            f"{amount:g} {symbol} on {network} to {recipient[:6]}...{recipient[-4:]} (test wallet refused it)")


def check_pipeline():
    from data_analytics.data_report import build_data_report, quoted_passages
    from data_science.compliance import assert_educational
    from tools.report_generator import fetch_and_analyse

    analysis = fetch_and_analyse("ETH", log_fn=lambda _msg: None)
    info = analysis["data_summary"]["token_info"]
    if "contract address" not in str(info.get("dex_pair_match")):
        raise RuntimeError(f"ETH pool was not found by contract address: {info.get('dex_pair_match')}")
    if not info.get("market_cap_usd"):
        raise RuntimeError("CoinGecko returned no market cap for ETH")
    if len(analysis["risk_checks"]) != 8:
        raise RuntimeError(f"expected 8 risk checks, got {len(analysis['risk_checks'])}")
    # A paid write-up is only worth selling when every source answers
    # Futures venues are checked from the server's location by check_sources
    failed = {k: v for k, v in (analysis["data_summary"].get("source_errors") or {}).items()
              if not k.endswith("futures")}
    if failed:
        raise RuntimeError("sources failed for ETH: " + "; ".join(f"{k} ({v[:80]})" for k, v in failed.items()))
    missing = [c["name"] for c in analysis["risk_checks"] if c["status"] == "no_data" and c["key"] != "leverage"]
    if missing:
        raise RuntimeError(f"ETH risk checks with no data: {', '.join(missing)}")
    assert_educational(build_data_report("ETH", analysis["data_summary"], "monitor run"),
                       quoted=quoted_passages(analysis["data_summary"]))
    return f"ETH data fetched (main pool {info.get('dex')} on {info.get('chain')}); report passes the advice check"


def check_sources():
    """Every data source answered on the server's last refresh. Read from the
    status file the server publishes, not fetched from here: exchanges refuse
    some locations, and only the server's location decides what a report gets.
    A machine that has just started writes its first file a few minutes in, so
    a missing file is waited for before it counts as a failure."""
    import datetime

    deadline = time.time() + int(os.getenv("MONITOR_SOURCES_WAIT_SECONDS") or "600")
    while True:
        resp = requests.get(f"{SITE}/status/sources.json", timeout=30)
        if resp.status_code == 200 or time.time() > deadline:
            break
        time.sleep(30)
    if resp.status_code != 200:
        raise RuntimeError(f"no source status published (HTTP {resp.status_code}); the refresher may not be running")
    status = resp.json()
    age = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(status["checked_at"])
    if age > datetime.timedelta(minutes=45):
        raise RuntimeError(f"source status is {age.seconds // 60} minutes old; the refresher has stopped")
    problems = status.get("problems") or {}
    if problems:
        raise RuntimeError("sources not answering: " + "; ".join(f"{k}: {', '.join(v)}" for k, v in problems.items()))
    return f"every source answered for all {len(status.get('chains') or [])} featured chains at {status['checked_at'][:16]} UTC"


def run(full):
    checks = [("DNS", check_dns), ("Site health", check_health), ("Payment networks", check_payment_networks)]
    if full:
        checks += [("Pages in a browser", check_pages), ("Paying in a browser", check_paying),
                   ("Data pipeline", check_pipeline),
                   ("Data sources", check_sources)]
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
