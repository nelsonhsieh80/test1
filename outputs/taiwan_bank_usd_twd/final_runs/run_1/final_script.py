import re
import sys
from datetime import date
from html import unescape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar


RUN_DIR = Path(__file__).resolve().parent
LOG_PATH = RUN_DIR / "final_script_log.txt"
OFFICIAL_CSV_URL = "https://rate.bot.com.tw/xrt/flcsv/0/day?Lang=zh-TW"
FALLBACK_URL = "https://www.findrate.tw/bank/29/"


def log(message):
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)


def fetch(url):
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(request, timeout=60) as response:
        raw = response.read()
        content_type = response.headers.get("Content-Type", "")
    encoding = "utf-8"
    if "charset=" in content_type:
        encoding = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
    return raw.decode(encoding, errors="replace")


def parse_findrate(html):
    text = unescape(html)
    date_match = re.search(r'id="rate_date"[^>]*>\s*([0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2})\s*</a>', text, re.S)
    if not date_match:
        raise RuntimeError("Could not find fallback update time")
    updated_at = date_match.group(1)

    row_match = re.search(
        r'<tr[^>]*>\s*<td\s+class="flag".*?美金\s+USD.*?</td>\s*'
        r'<td[^>]*>\s*([^<]+)\s*</td>\s*'
        r'<td[^>]*>\s*([^<]+)\s*</td>\s*'
        r'<td[^>]*>\s*([^<]+)\s*</td>\s*'
        r'<td[^>]*>\s*([^<]+)\s*</td>',
        text,
        re.S,
    )
    if not row_match:
        raise RuntimeError("Could not find USD row in fallback page")
    return {
        "updated_at": updated_at,
        "cash_buy": row_match.group(1).strip(),
        "cash_sell": row_match.group(2).strip(),
        "spot_buy": row_match.group(3).strip(),
        "spot_sell": row_match.group(4).strip(),
    }


def main():
    LOG_PATH.write_text("", encoding="utf-8")
    today = date.today().isoformat()
    log("step 1 action: Attempted official Bank of Taiwan listed exchange rate CSV endpoint")
    try:
        official = fetch(OFFICIAL_CSV_URL)
    except URLError as exc:
        official = ""
        log(f"step 1 result: official fetch failed: {exc}")

    if "Challenge Validation" in official or not official.strip():
        log("step 1 result: official endpoint returned Challenge Validation, not exchange-rate data")
    else:
        log("step 1 result: official endpoint returned data, but CSV parsing was not implemented in this fallback run")

    log("step 2 action: Fetched third-party page that states it synchronizes Taiwan Bank listed rates")
    fallback = fetch(FALLBACK_URL)
    data = parse_findrate(fallback)
    is_today = data["updated_at"].startswith(today)
    log(f"step 2 result: fallback update time: {data['updated_at']}; today: {today}; is_today: {is_today}")
    log("step 3 action: Located USD row and extracted cash and spot buying/selling rates")
    log(
        "FINAL DATA: "
        f"source={FALLBACK_URL}; updated_at={data['updated_at']}; "
        f"cash_buy={data['cash_buy']}; cash_sell={data['cash_sell']}; "
        f"spot_buy={data['spot_buy']}; spot_sell={data['spot_sell']}; "
        f"today_verified={is_today}"
    )
    if not is_today:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
