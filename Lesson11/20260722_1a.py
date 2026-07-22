# 匯入 Playwright 相關型別與同步 API
from playwright.sync_api import sync_playwright, Playwright, Browser, Page


def crawl(p: Playwright) -> None:
  # 啟動 Chromium 瀏覽器並開啟新頁面
  browser: Browser = p.chromium.launch()
  page: Page = browser.new_page()

  # 導航到維基百科首頁
  page.goto("https://zh.wikipedia.org")

  # 填入搜尋文字到搜尋框
  page.locator("#searchInput").fill("臺灣")

  # 截圖留存
  page.screenshot(path="screenshot.png")

  # 按下 Enter 觸發搜尋
  page.keyboard.press("Enter")

  # 等待網路閒置，確保頁面完全載入
  page.wait_for_load_state("networkidle")

  # 取得並輸出搜尋結果頁面的第一筆標題
  first_heading: str = page.locator("#firstHeading").inner_text()
  print(f"搜尋主題:{first_heading}")

  # 取得並輸出摘要內容（前 100 字元）
  content: str = page.locator("#mw-content-text p").first.inner_text()
  print(f"摘要: {content[:100]}")

  # 返回上一頁（首頁）
  page.go_back()
  page.wait_for_load_state("networkidle")
  print(f"返品首頁:{page.title()}")

  # 關閉瀏覽器
  browser.close()


# 使用 sync_playwright 作為上下文管理器，自動處理 Playwright 啟動與關閉
with sync_playwright() as p:
  crawl(p)