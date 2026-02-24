#  Taiwan Government Procurement API (台灣政府採購網資料 API)

##  產品簡介 (Product Overview)
這是一個專為開發者設計的**政府採購資料自動化擷取服務**。


###  核心功能 (Key Features)

*    自動化資料擷取 (Automated Scraping)<br>
    *   內建爬蟲核心，模擬瀏覽器行為。<br>
    *   支援關鍵字搜尋與多頁面翻頁功能。
*    反反爬蟲機制 (Anti-Anti-Scraping)<br>
    *   整合偽裝標頭 (User-Agent Rotation) 與自動延遲機制。<br>
    *   使用 Selenium + undetected-chromedriver 技術繞過 WAF 檢測。
*    標準化 API 介面 (Standardized RESTful API)<br>
    *   提供清晰的 HTTP GET 接口。<br>
    *   回傳格式統一為 JSON，方便前端與資料分析使用。
*    資料結構化 (Structured Data Models)<br>
    *   自動將非結構化的網頁 HTML 轉換為嚴謹的 Python 物件 (Pydantic Models)。<br>
    *   欄位包含：機關名稱、標案名稱、預算金額、公告日期、截標日期等核心資訊。

###  技術架構 (Tech Stack)

*   **後端框架**: [FastAPI](https://fastapi.tiangolo.com/) (高效能、易於開發的 Python Web 框架)
*   **爬蟲核心**: [Selenium](https://www.selenium.dev/) (自動化瀏覽器控制)
*   **資料解析**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) (HTML 解析)
*   **資料驗證**: [Pydantic](https://docs.pydantic.dev/) (資料格式定義與驗證)

###  快速開始 (Quick Start)

### 1. 安裝依賴 (Installation)

確保您的環境已安裝 Python 3.9+ 與 Chrome 瀏覽器。

```bash
pip install -r requirements.txt
```

### 2. 啟動服務 (Start Server)

```bash
python main.py
```
伺服器將啟動於 `http://0.0.0.0:8000`。

### 3. 使用 API (Usage)

發送 GET 請求即可獲取標案資料：

**取得所有標案 (預設)**
```
GET http://localhost:8000/api/tenders
```

**搜尋特定標案 (例如：工程)**
```
GET http://localhost:8000/api/tenders?tenderName=工程
```

##  資料格式範例 (Response Example)

```json
[
  {
    "id": 1,
    "agency_name": "臺北市政府工務局",
    "tender_name": "113年度道路維護工程",
    "tender_mode": "公開招標",
    "procurement_nature": "工程類",
    "announcement_date": "113/05/20",
    "deadline": "113/06/01",
    "budget": "5000000"
  }
]
```

##  注意事項 (Disclaimer)
本專案僅測試用，近期會下架-Derek