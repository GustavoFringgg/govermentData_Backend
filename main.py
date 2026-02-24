from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import TenderItem
from scraper import Scraper
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO) # looger 設定
logger = logging.getLogger(__name__)

app = FastAPI(title="Government Tender Scraper API") # FastAPI 名稱

# Configure CORS
origins = [
    "*" # Allow all for development convenience
    ]

""" "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:5173",  """

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, #設定是否允許前端傳送 Cookies 或 驗證資訊（如 HTTP 認證）到後端。
    allow_methods=["*"], #設定允許的 HTTP 方法
    allow_headers=["*"], #不限制，允許所有標頭
)



@app.get("/health")
@app.head("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/tenders", response_model=List[TenderItem])
async def get_tenders(tenderName: Optional[str] = None): 

    scraper = Scraper(headless=True) 
    # 初始化 scraper 建立新的物件 
    # headless=True: 是否以無頭模式運行 程式會在背景執行瀏覽器 不會顯示
    # 爬完資料後關閉瀏覽器
    try:
        data = scraper.scrape_data(keyword=tenderName)
        # 也可以寫成
        # data = scraper.scrape_data(tenderName) 但為了可讀性 需要keyword = tenderName
        return data
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__": 
    #「如果是直接執行這個檔案 (python main.py)，才執行下面的程式碼。」
    # 用途:避免副作用
    # if run python main.py then run uvicorn
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render 會自動注入 PORT 環境變數
    uvicorn.run("main:app"   # main.py 裡的 app 物件
    , host="0.0.0.0",        # 接受所有 IP 連線（不只是本機）
    port=port,               # 使用環境變數的 Port
    reload=False)            # 正式環境不要開 reload


