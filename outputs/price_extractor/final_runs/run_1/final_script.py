"""Reusable product price extractor."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


DEFAULT_URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
PRICE_RE = re.compile(
    r"(?:NT\$|NTD|TWD|US\$|USD|HK\$|\$|€|£|¥|￥|Rs\.?|RM|S\$)\s?[\d,]+(?:\.\d{1,2})?|[\d,]+(?:\.\d{1,2})?\s?(?:元|円|yen|dollars?)",
    re.IGNORECASE,
)


def log_step(log_path: Path, step: int, message: str) -> None:
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"step {step} action: {message}\n")


def text_or_none(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = " ".join(value.split())
        return cleaned or None
    return None


def iter_jsonld_values(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        values = []
        graph = data.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                values.extend(iter_jsonld_values(item))
        values.append(data)
        return values
    if isinstance(data, list):
        values = []
        for item in data:
            values.extend(iter_jsonld_values(item))
        return values
    return []


def price_from_offer(offer: Any) -> str | None:
    if isinstance(offer, list):
        for item in offer:
            price = price_from_offer(item)
            if price:
                return price
    if isinstance(offer, dict):
        price = text_or_none(offer.get("price")) or text_or_none(offer.get("lowPrice"))
        currency = text_or_none(offer.get("priceCurrency"))
        if price and currency:
            return f"{currency} {price}"
        if price:
            return price
    return None


def extract_from_jsonld(jsonld_blocks: list[str]) -> tuple[str | None, str | None]:
    for block in jsonld_blocks:
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        for item in iter_jsonld_values(parsed):
            item_type = item.get("@type")
            types = item_type if isinstance(item_type, list) else [item_type]
            looks_like_product = any(str(value).lower() == "product" for value in types)
            if not looks_like_product and "offers" not in item:
                continue
            name = text_or_none(item.get("name"))
            price = price_from_offer(item.get("offers"))
            if name or price:
                return name, price
    return None, None


def extract_product_price(product_url: str, output_dir: str = ".") -> dict[str, str]:
    """Extract product name, current price, and extraction time from a URL.

    Args:
        product_url: Product page URL to visit and parse.
        output_dir: Directory where screenshots and final_script_log.txt are written.
    """
    run_dir = Path(output_dir).resolve()
    screenshots_dir = run_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "final_script_log.txt"
    log_path.write_text("", encoding="utf-8")
    log_step(log_path, 0, f"params: product_url={product_url}")

    extracted_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1800})
        try:
            log_step(log_path, 1, "open product page")
            page.goto(product_url, wait_until="domcontentloaded", timeout=45000)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                log_step(log_path, 2, "network idle timeout ignored after DOM loaded")
            page.screenshot(path=str(screenshots_dir / "final_execution_1_loaded_page.png"))

            log_step(log_path, 3, "parse structured data and visible page text")
            jsonld_blocks = page.locator('script[type="application/ld+json"]').evaluate_all(
                "els => els.map(el => el.textContent || '')"
            )
            name, price = extract_from_jsonld(jsonld_blocks)

            if not name:
                og_title = page.locator('meta[property="og:title"]').first
                if og_title.count():
                    name = text_or_none(og_title.get_attribute("content"))
            if not name:
                h1 = page.locator("h1").first
                if h1.count():
                    name = text_or_none(h1.inner_text(timeout=5000))
            if not name:
                name = text_or_none(page.title()) or "UNKNOWN"

            if not price:
                candidate_texts = page.locator("body").inner_text(timeout=10000).splitlines()
                for line in candidate_texts:
                    match = PRICE_RE.search(line)
                    if match:
                        price = match.group(0).strip()
                        break
            if not price:
                price = "UNKNOWN"

            page.screenshot(path=str(screenshots_dir / "final_execution_2_parsed_result.png"))
        finally:
            browser.close()

    result = {
        "product_name": name,
        "current_price": price,
        "extracted_at": extracted_at,
    }
    log_step(log_path, 4, "final result: " + json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract product name, current price, and extraction time from a product URL.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="Product page URL to scrape.")
    parser.add_argument("--output-dir", default=".", help="Directory for screenshots and final_script_log.txt.")
    args = parser.parse_args()
    extract_product_price(args.url, args.output_dir)


if __name__ == "__main__":
    main()
