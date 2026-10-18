"""
Chart screenshot adapter: the only module that drives a headless browser.

Off state: with SCREENSHOTS_ENABLED=false, or with Playwright not installed,
capture_dexscreener_chart() returns None and the report says no chart was
captured. A missing chart never stops a report.
"""
import logging

from config import IMAGES_DIR, ROOT_DIR, SETTINGS

log = logging.getLogger(__name__)


def capture_dexscreener_chart(token_symbol, dex_url):
    """Capture the DexScreener page for a pair. Returns the image path relative
    to the project root (so reports stay portable across machines), or None."""
    if not SETTINGS.screenshots_enabled:
        return None
    if not dex_url:
        log.info("Skipping screenshot for %s: no DexScreener URL.", token_symbol)
        return None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.warning("Playwright is not installed; skipping the chart screenshot.")
        return None

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    file_path = IMAGES_DIR / f"{token_symbol}_chart.png"
    try:
        with sync_playwright() as p:
            # Firefox gets past basic Cloudflare checks more often than headless Chromium
            browser = p.firefox.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            )
            # domcontentloaded, not load: the chart's websocket never lets "load" settle
            page.goto(dex_url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_selector("canvas", state="attached", timeout=15000)
            except Exception:
                pass  # some pairs render no canvas; capture the page anyway
            # The candles arrive over the websocket after the canvas exists
            page.wait_for_timeout(12000)
            page.screenshot(path=str(file_path), full_page=False)
            browser.close()
        return str(file_path.relative_to(ROOT_DIR))
    except Exception as e:
        log.warning("Chart screenshot failed for %s: %s", token_symbol, e)
        return None
