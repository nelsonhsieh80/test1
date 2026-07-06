import re
import sys
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright


RUN_DIR = Path(__file__).resolve().parent
SCREENSHOTS = RUN_DIR / "screenshots"
LOG_PATH = RUN_DIR / "final_script_log.txt"
URL = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def log(message):
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)


def screenshot(page, step, action):
    path = SCREENSHOTS / f"final_execution_{step}_{action}.png"
    page.screenshot(path=str(path))
    log(f"step {step} screenshot: {path}")
    return path


def main():
    LOG_PATH.write_text("", encoding="utf-8")
    SCREENSHOTS.mkdir(exist_ok=True)
    today_iso = date.today().isoformat()
    today_slash = today_iso.replace("-", "/")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=CHROME,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(viewport={"width": 1280, "height": 1800})
        page = context.new_page()

        log("step 1 action: Open Bank of Taiwan listed exchange rate page")
        page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(45000)
        if "Challenge" in page.title():
            page.reload(wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(5000)
        page.wait_for_selector("table tbody tr", timeout=90000)
        screenshot(page, 1, "bank_of_taiwan_page")

        body_text = page.locator("body").inner_text(timeout=10000)
        title = page.title()
        if "臺灣銀行牌告匯率" not in title and "臺灣銀行牌告匯率" not in body_text:
            raise RuntimeError("Did not reach Bank of Taiwan listed exchange rate page")
        log(f"step 1 result: reached official page; title={title}; url={page.url}")

        log("step 2 action: Confirm today's listed exchange-rate date and quote timestamp")
        date_line = next((line.strip() for line in body_text.splitlines() if today_slash in line and "牌告匯率" in line), "")
        time_match = re.search(r"牌價最新掛牌時間：\s*([0-9/]+\s+[0-9:]+)", body_text)
        if not date_line or not time_match:
            raise RuntimeError("Could not verify today's date and quote time")
        quote_time = time_match.group(1)
        if not quote_time.startswith(today_slash):
            raise RuntimeError(f"Quote time is not today: {quote_time}")
        screenshot(page, 2, "today_quote_time")
        log(f"step 2 result: date_line={date_line}; quote_time={quote_time}")

        log("step 3 action: Locate USD row and extract cash and spot buying/selling rates")
        usd_row = page.locator("table tbody tr", has_text="美金").first
        cells = [cell.strip() for cell in usd_row.locator("td").all_text_contents()]
        if len(cells) < 5:
            raise RuntimeError(f"Unexpected USD row format: {cells}")
        cash_buy, cash_sell, spot_buy, spot_sell = cells[1], cells[2], cells[3], cells[4]
        screenshot(page, 3, "usd_row_rates")
        log(
            "step 3 result: USD row found; "
            f"cash_buy={cash_buy}; cash_sell={cash_sell}; spot_buy={spot_buy}; spot_sell={spot_sell}"
        )
        log(
            "FINAL DATA: "
            f"source={URL}; quote_time={quote_time}; currency=USD/TWD; "
            f"cash_buy={cash_buy}; cash_sell={cash_sell}; spot_buy={spot_buy}; spot_sell={spot_sell}"
        )
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
