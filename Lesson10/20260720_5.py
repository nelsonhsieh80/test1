"""專案 01：開啟真實網頁，檢查標題並留下截圖。"""

import argparse  # 解析命令列參數
from pathlib import Path  # 處理檔案路徑

from playwright.sync_api import sync_playwright  # Playwright 自動化測試


# 目標網址與輸出目錄
URL = "https://example.com/"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def check_website(browser_name: str = "chromium") -> None:
    """開啟瀏覽器、載入網頁、檢查標題、截圖並輸出結果。"""
    OUTPUT_DIR.mkdir(exist_ok=True)  # 確保輸出資料夾存在

    with sync_playwright() as playwright:
        # 根據參數選取瀏覽器類型（chromium / firefox / webkit）
        browser_type = getattr(playwright, browser_name)
        browser = browser_type.launch(headless=True)  # 無頭模式執行
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        # 導航到目標網址，等待 DOM 載入完成
        response = page.goto(URL, wait_until="domcontentloaded")
        # 找出標題為 "Example Domain" 的 heading 元素並取得文字
        heading = page.get_by_role("heading", name="Example Domain").inner_text()
        # 截圖儲存
        screenshot = OUTPUT_DIR / f"homepage_{browser_name}.png"
        page.screenshot(path=screenshot, full_page=True)

        # 輸出結果
        print(f"瀏覽器: {browser_name}")
        print(f"HTTP 狀態: {response.status if response else '無回應'}")
        print(f"頁面標題: {page.title()}")
        print(f"主標題: {heading}")
        print(f"截圖: {screenshot}")
        browser.close()


if __name__ == "__main__":
    # 命令列參數：--browser 可指定 chromium / firefox / webkit
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--browser", choices=["chromium", "firefox", "webkit"], default="chromium"
    )
    args = parser.parse_args()
    check_website(args.browser)