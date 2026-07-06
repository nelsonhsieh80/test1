from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(__file__).parent

with sync_playwright() as p:
    browser = p.firefox.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 1800})
    page.goto("https://rate.bot.com.tw/xrt?Lang=zh-TW", wait_until="networkidle", timeout=60000)
    page.screenshot(path=str(out / "explore_rates_page.png"))
    print("URL:", page.url)
    print("TITLE:", page.title())
    print("H1:", page.locator("h1").first.text_content(timeout=10000))
    print("TIMESTAMP:", page.locator(".time").first.text_content(timeout=10000))
    print("HEADERS:", [h.strip() for h in page.locator("table thead th").all_text_contents()])
    usd_row = page.locator("table tbody tr", has_text="美金").first
    print("USD_ROW_TEXT:", " | ".join(part.strip() for part in usd_row.locator("td").all_text_contents()))
    print("ARIA_START")
    print(page.locator("body").aria_snapshot(timeout=10000)[:5000])
    print("ARIA_END")
    browser.close()
