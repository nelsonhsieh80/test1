from playwright.sync_api import sync_playwright,Playwright,Browser,Page


def crawl(p:Playwright) -> None:
  browser:Browser = p.chromium.launch()
  page:Page = browser.new_page()

  # 頁面載入等待 domcontentloaded，避免 networkidle 超時
  page.goto("https://zh.wikipedia.org", wait_until="domcontentloaded")

  # 除錯：印出頁面網址與標題
  print(f"[DEBUG] page.url: {page.url}")
  print(f"[DEBUG] page.title: {page.title()}")

  # 確認 placeholder 為「搜尋維基百科」的元素數量
  search_boxes = page.get_by_placeholder("搜尋維基百科")
  count = search_boxes.count()
  print(f"[DEBUG] placeholder '搜尋維基百科' 元素數量: {count}")

  # 使用較穩定的 locator：優先 searchbox role， fallback 到 input[name]
  search_input = page.get_by_role("searchbox")
  if search_input.count() == 0:
    search_input = page.locator('input[name="search"]')
  if search_input.count() == 0:
    # 最後 fallback：直接用 placeholder，取第 1 個
    search_input = page.get_by_placeholder("搜尋維基百科")

  print(f"[DEBUG] 最終使用的 locator 匹配數量: {search_input.count()}")

  # 等待搜尋框可見後再填入
  search_input.first.wait_for(state="visible")
  search_input.first.fill("臺灣")

  page.screenshot(path="screenshot.png")
  page.keyboard.press("Enter")
  page.wait_for_load_state("networkidle")
  first_heading:str = page.locator("#firstHeading").inner_text()
  print(f"搜尋主題:{first_heading}")

  content:str = page.locator("#mw-content-text p").first.inner_text()
  print(f"摘要: {content[:100]}")
  page.go_back()
  page.wait_for_load_state("networkidle")
  print(f"回首頁:{page.title()}")
  browser.close()


with sync_playwright() as p:
  crawl(p)