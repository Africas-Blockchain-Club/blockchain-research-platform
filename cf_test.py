import os
from playwright.sync_api import sync_playwright

def test_cf():
    with sync_playwright() as p:
        # User Agent sometimes helps, also using WebKit or Firefox
        for browser_type in [p.firefox, p.chromium]:
            try:
                browser = browser_type.launch(headless=True)
                page = browser.new_page(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                print(f"Testing {browser_type.name}...")
                response = page.goto('https://dexscreener.com/solana/5mbkmcswdmsdizx1cjm3wruy2xsp2qyyq7xtnnxdbxmy', wait_until='domcontentloaded', timeout=15000)
                page.wait_for_timeout(5000)
                page.screenshot(path=f'test_{browser_type.name}.png')
                title = page.title()
                print(f"Title: {title}")
                browser.close()
            except Exception as e:
                print(e)

test_cf()
