# __2026_06_17_playwirght__
華梵板橋爬蟲
課程內容
## 上課網址
https://meet.google.com/ifx-tbsg-xac

---

## 網站健康檢查工具（Lesson10／20260720_5）

### 安裝

```bash
# 建議使用 uv（取代 pip）
uv sync

# 安裝 Playwright 瀏覽器
uv run playwright install chromium
```

### CLI 執行

```bash
# 使用預設瀏覽器（chromium）
uv run python Lesson10/20260720_5.py

# 指定瀏覽器
uv run python Lesson10/20260720_5.py --browser firefox
uv run python Lesson10/20260720_5.py --browser webkit
```

### GUI 執行

```bash
uv run python Lesson10/gui.py
```

### 測試

```bash
uv run pytest Lesson10/test_20260720_5.py -v
```

### 專案結構

```
Lesson10/
├── 20260720_5.py              # CLI + 核心函式（CheckResult、check_website_core）
├── gui.py                     # tkinter 圖形介面
├── test_20260720_5.py         # 基本測試
├── output/                    # 截圖輸出資料夾
└── form_demo.html             # 表單範例（20260720_4.py 使用）
```
