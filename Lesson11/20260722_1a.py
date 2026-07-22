# 匯入 Playwright 相關型別與同步 API
from datetime import datetime
from playwright.sync_api import sync_playwright, Playwright, Browser, Page

# 常數設定
BASE_URL: str = "https://zh.wikipedia.org"


def crawl(p: Playwright) -> None:
  browser: Browser = p.chromium.launch(headless=True)
  page: Page = browser.new_page()
  try:
    # 導航到維基百科首頁，使用 domcontentloaded 避免逾時
    page.goto(BASE_URL, wait_until="domcontentloaded")

    # 使用較穩定的 locator：優先 searchbox role，fallback 到 #searchInput
    search_input = page.get_by_role("searchbox")
    if search_input.count() == 0:
      search_input = page.locator("#searchInput")

    # 等待搜尋框可見後再填入
    search_input.first.wait_for(state="visible")
    search_input.first.fill("臺灣")

    # 截圖留存（依時間戳命名，避免覆寫）
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    page.screenshot(path=f"screenshot_{timestamp}.png")

    # 按下 Enter 觸發搜尋
    page.keyboard.press("Enter")

    # 等待頁面載入（改用 domcontentloaded 取代 networkidle）
    page.wait_for_load_state("domcontentloaded")

    # 取得並輸出搜尋結果頁面的第一筆標題
    first_heading: str = page.locator("#firstHeading").inner_text()
    print(f"搜尋主題:{first_heading}")

    # 取得並輸出摘要內容（前 100 字元）
    content: str = page.locator("#mw-content-text p").first.inner_text()
    print(f"摘要: {content[:100]}")

    # 返回上一頁（首頁）
    page.go_back()
    page.wait_for_load_state("domcontentloaded")
    print(f"返品首頁:{page.title()}")

  except Exception as e:
    print(f"發生錯誤: {e}")
  finally:
    browser.close()


# 使用 sync_playwright 作為上下文管理器，自動處理 Playwright 啟動與關閉
with sync_playwright() as p:
  crawl(p)