from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(__file__).parent
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=chrome)
    context = browser.new_context(viewport={"width": 1280, "height": 1800})
    page = context.new_page()
    page.goto("https://www.ptt.cc/bbs/Gossiping/index.html", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)
    print("INITIAL_URL:", page.url)
    print("INITIAL_TITLE:", page.title())
    print("INITIAL_TEXT_START")
    print(page.locator("body").inner_text(timeout=10000)[:3000])
    print("INITIAL_TEXT_END")
    page.screenshot(path=str(out / "explore_initial.png"))

    yes = page.locator("button:has-text('我同意，我已年滿十八歲')")
    if yes.count() > 0:
        print("AGE_GATE: button found")
        yes.click()
        page.wait_for_load_state("networkidle", timeout=60000)
    else:
        link_yes = page.locator("text=我同意，我已年滿十八歲")
        if link_yes.count() > 0:
            print("AGE_GATE: link/text found")
            link_yes.click()
            page.wait_for_load_state("networkidle", timeout=60000)
        else:
            print("AGE_GATE: none")

    page.screenshot(path=str(out / "explore_after_age.png"))
    print("FINAL_URL:", page.url)
    print("FINAL_TITLE:", page.title())
    print("FINAL_TEXT_START")
    print(page.locator("body").inner_text(timeout=10000)[:5000])
    print("FINAL_TEXT_END")
    rows = page.locator(".r-ent")
    print("ROW_COUNT:", rows.count())
    for i in range(min(12, rows.count())):
        row = rows.nth(i)
        title = row.locator(".title").inner_text(timeout=10000).strip().replace("\n", " ")
        push = row.locator(".nrec").inner_text(timeout=10000).strip()
        print(f"ROW_{i+1}: push={push!r}; title={title!r}")
    print("ARIA_START")
    print(page.locator("body").aria_snapshot(timeout=10000)[:5000])
    print("ARIA_END")
    browser.close()
