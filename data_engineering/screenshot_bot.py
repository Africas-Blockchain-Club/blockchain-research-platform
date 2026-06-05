import os
from playwright.sync_api import sync_playwright

def capture_dexscreener_chart(token_symbol, dex_url):
    """
    Uses a headless Playwright browser to capture the DexScreener chart.
    """
    # Ensure the images directory exists
    images_dir = os.path.join(os.getcwd(), "data", "images")
    os.makedirs(images_dir, exist_ok=True)
    
    file_path = os.path.join(images_dir, f"{token_symbol}_chart.png")
    
    if not dex_url:
        print(f"Skipping screenshot for {token_symbol}: No DexScreener URL provided.")
        return None

    print(f"Capturing DexScreener chart for {token_symbol}...")
    try:
        with sync_playwright() as p:
            # Firefox often bypasses basic Cloudflare Turnstile blocks better than Chromium headless
            browser = p.firefox.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0")
            
            # Navigate to the DexScreener pair using domcontentloaded to avoid websocket hang
            page.goto(dex_url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for the TradingView chart canvas to appear and render
            try:
                page.wait_for_selector("canvas", state="attached", timeout=15000)
            except Exception:
                pass  # Canvas might not appear for some tokens, continue anyway
            
            # Give the chart extra time to paint candlesticks via WebSocket data feed
            page.wait_for_timeout(12000)
            
            # Optional: We could target just the chart container, but capturing the whole page 
            # provides the sentiment and holistic info the user requested.
            page.screenshot(path=file_path, full_page=False)
            
            browser.close()
            
        print(f"Successfully saved chart screenshot for {token_symbol} to {file_path}")
        return file_path
    
    except Exception as e:
        print(f"Error capturing screenshot for {token_symbol}: {e}")
        return None
