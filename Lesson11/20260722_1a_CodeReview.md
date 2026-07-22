# Code Review: `20260722_1a.py`

## 優點

1. **型別提示**：函式參數與區域變數皆有型別註記（`Playwright`、`Browser`、`Page`），提升可讀性。
2. **簡潔流程**：程式碼行數少，爬取流程直觀易懂。
3. **上下文管理器**：使用 `sync_playwright()` 確保 Playwright 正確啟動與關閉。

## 建議改進

| 類別 | 建議 | 說明 |
|------|------|------|
| **穩定性** | `goto` 加入 `wait_until` 參數 | 預設 `load` 可能因網路慢而逾時，建議用 `domcontentloaded`（參見 `20260722_1.py` 的做法） |
| **穩定性** | 填入搜尋文字前應等待元素可見 | 使用 `page.locator("#searchInput").wait_for(state="visible")` 可避免元素未渲染就操作的錯誤 |
| **安全性** | 避免使用 `networkidle` | `networkidle` 在長輪詢頁面可能永不觸發，可改用 `domcontentloaded` 或 `load` |
| **可維護性** | 將超連結字串抽成常數或設定 | `BASE_URL = "https://zh.wikipedia.org"` 便於日後修改 |
| **例外處理** | 缺少 `try/except/finally` | 若中間步驟拋錯（如元素找不到），`browser.close()` 將不會被執行，建議將 `browser.close()` 放在 `finally` 區塊 |
| **覆蓋問題** | `screenshot.png` 固定檔名 | 每次執行會覆寫同一檔案，可依時間戳動態命名（如 `screenshot_20260722.png`） |
| **Loator 可靠性** | `#searchInput` 可能不穩定 | 建議搭配 `get_by_placeholder("搜尋維基百科")` 或 `get_by_role("searchbox")` 作為 fallback |
| **無頭模式** | 未啟用 headless | 若不需要看到瀏覽器畫面，建議 `headless=True` 以節省資源 |

## 改寫範例（擷取重點）

```python
def crawl(p: Playwright) -> None:
  browser = p.chromium.launch()
  page = browser.new_page()
  try:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    search_input = page.get_by_role("searchbox")
    if search_input.count() == 0:
      search_input = page.locator("#searchInput")
    search_input.first.wait_for(state="visible")
    search_input.first.fill("臺灣")
    # ... 其餘邏輯 ...
  except Exception as e:
    print(f"發生錯誤: {e}")
  finally:
    browser.close()
```

## 與 `20260722_1.py` 比較

`20260722_1a.py` 是 `20260722_1.py` 的簡化版，移除了除錯輸出與多種 locator fallback 邏輯。若目標是學習 Playwright 基礎流程，`1a` 版本足夠清晰；若作為正式爬蟲，建議參考 `1.py` 的做法加入容錯機制。

## 總結

整體程式碼簡潔且方向正確，加入適度的容錯與等待機制後即可應付更多實際情境。
