import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


RUN_DIR = Path(__file__).resolve().parent
SCREENSHOTS = RUN_DIR / "screenshots"
LOG_PATH = RUN_DIR / "final_script_log.txt"
URL = "https://www.ptt.cc/bbs/Gossiping/index.html"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def log(message):
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)


def screenshot(page, step, action):
    path = SCREENSHOTS / f"final_execution_{step}_{action}.png"
    page.screenshot(path=str(path))
    log(f"step {step} screenshot: {path}")


def main():
    LOG_PATH.write_text("", encoding="utf-8")
    SCREENSHOTS.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME)
        context = browser.new_context(viewport={"width": 1280, "height": 1800})
        page = context.new_page()

        log("step 1 action: Navigate to PTT Gossiping board homepage")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1000)
        screenshot(page, 1, "initial_navigation")
        log(f"step 1 result: url={page.url}; title={page.title()}")

        log("step 2 action: Use the site's age confirmation control if it appears")
        age_button = page.locator("button:has-text('我同意，我已年滿十八歲')")
        if age_button.count() > 0:
            age_button.click()
            page.wait_for_load_state("networkidle", timeout=60000)
            log("step 2 result: clicked age confirmation button")
        else:
            log("step 2 result: age confirmation button did not appear")
        screenshot(page, 2, "after_age_confirmation")

        log("step 3 action: Confirm page is the Gossiping board homepage")
        page.wait_for_selector(".r-ent", timeout=60000)
        heading_text = page.locator("#topbar .board").inner_text(timeout=10000).strip()
        if "Gossiping" not in heading_text:
            raise RuntimeError(f"Expected Gossiping board, got: {heading_text}")
        log(f"step 3 result: board heading={heading_text}; url={page.url}; title={page.title()}")
        screenshot(page, 3, "gossiping_homepage")

        log("step 4 action: Extract first 10 visible article entries in page order")
        rows = page.locator(".r-ent")
        if rows.count() < 10:
            raise RuntimeError(f"Expected at least 10 article rows, found {rows.count()}")
        articles = []
        for i in range(10):
            row = rows.nth(i)
            title = " ".join(row.locator(".title").inner_text(timeout=10000).split())
            push = row.locator(".nrec").inner_text(timeout=10000).strip()
            articles.append((push, title))
        screenshot(page, 4, "first_10_articles")
        log("step 4 result: extracted 10 visible article entries")

        log("step 5 action: Record each article title and push count exactly as displayed")
        for index, (push, title) in enumerate(articles, 1):
            display_push = push if push else ""
            log(f"article {index}: push={display_push!r}; title={title}")
        final_data = " | ".join(
            f"{index}. push={(push if push else '')!r}, title={title}"
            for index, (push, title) in enumerate(articles, 1)
        )
        log(f"FINAL DATA: {final_data}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
