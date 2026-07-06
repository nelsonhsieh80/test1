from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(__file__).parent
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=chrome,
        args=["--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(viewport={"width": 1280, "height": 1800})
    page = context.new_page()
    page.goto("https://rate.bot.com.tw/xrt?Lang=zh-TW", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(45000)
    if "Challenge" in page.title():
        page.reload(wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(5000)
    page.screenshot(path=str(out / "explore_rates_page_chrome_headed.png"))
    print("URL:", page.url)
    print("TITLE:", page.title())
    print("BODY_START")
    print(page.locator("body").inner_text(timeout=10000)[:5000])
    print("BODY_END")
    rows = page.locator("table tbody tr")
    print("ROWS:", rows.count())
    usd = page.locator("table tbody tr", has_text="美金").first
    if usd.count():
        print("USD_ROW_TEXT:", " | ".join(part.strip() for part in usd.locator("td").all_text_contents()))
    browser.close()
