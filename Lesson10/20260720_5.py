"""專案 01：開啟真實網頁，檢查標題並留下截圖。"""

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import sync_playwright


URL = "https://example.com/"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


@dataclass
class CheckResult:
    url: str
    http_status: int | None = None
    response_time_ms: float | None = None
    page_title: str = ""
    main_heading: str = ""
    final_url: str = ""
    screenshot_path: str | None = None
    success: bool = True
    error_message: str = ""


def validate_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError(
            "網址不能空白。請輸入要檢查的網址（例如 https://example.com/）。"
        )
    if not url.startswith(("http://", "https://")):
        raise ValueError(
            f"網址格式不正確：{url}\n"
            "請以 http:// 或 https:// 開頭。\n"
            "範例：https://www.google.com/"
        )
    return url


def validate_timeout(timeout_str: str) -> int:
    raw = timeout_str.strip()
    try:
        timeout = int(raw)
    except ValueError:
        raise ValueError(
            f"Timeout 必須是整數數字（毫秒），你輸入的是「{raw}」。\n"
            "範例：30000（代表 30 秒）"
        )
    if timeout < 1000:
        raise ValueError(
            f"Timeout 至少需要 1000 毫秒（1 秒），你設定的是 {timeout} 毫秒。\n"
            "建議值：30000（30 秒）"
        )
    if timeout > 120000:
        raise ValueError(
            f"Timeout 不能超過 120000 毫秒（2 分鐘），你設定的是 {timeout} 毫秒。"
        )
    return timeout


def check_website_core(
    url: str,
    browser_name: str = "chromium",
    headless: bool = True,
    timeout_ms: int = 30000,
) -> CheckResult:
    OUTPUT_DIR.mkdir(exist_ok=True)
    result = CheckResult(url=url)

    try:
        with sync_playwright() as playwright:
            browser_type = getattr(playwright, browser_name)
            browser = browser_type.launch(headless=headless)
            page = browser.new_page(viewport={"width": 1280, "height": 720})

            start = time.monotonic()
            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            elapsed = (time.monotonic() - start) * 1000

            result.http_status = response.status if response else None
            result.response_time_ms = round(elapsed, 1)
            result.page_title = page.title()
            result.final_url = page.url

            try:
                heading = page.get_by_role("heading").first
                result.main_heading = heading.inner_text()
            except Exception:
                result.main_heading = ""

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot = OUTPUT_DIR / f"check_{timestamp}_{browser_name}.png"
            page.screenshot(path=screenshot, full_page=True)
            result.screenshot_path = str(screenshot)

            browser.close()
    except Exception as exc:
        result.success = False
        result.error_message = str(exc)

    return result


def check_website(browser_name: str = "chromium") -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, browser_name)
        browser = browser_type.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        response = page.goto(URL, wait_until="domcontentloaded")
        heading = page.get_by_role("heading", name="Example Domain").inner_text()
        screenshot = OUTPUT_DIR / f"homepage_{browser_name}.png"
        page.screenshot(path=screenshot, full_page=True)

        print(f"瀏覽器: {browser_name}")
        print(f"HTTP 狀態: {response.status if response else '無回應'}")
        print(f"頁面標題: {page.title()}")
        print(f"主標題: {heading}")
        print(f"截圖: {screenshot}")

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--browser", choices=["chromium", "firefox", "webkit"], default="chromium"
    )
    args = parser.parse_args()
    check_website(args.browser)
