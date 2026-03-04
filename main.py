from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routers import tenders,health

from services import tender_service
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO) # looger 設定

app = FastAPI(title="Government Tender Scraper API") # FastAPI 名稱
app.include_router(tenders.router)
app.include_router(health.router)

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




scheduler = AsyncIOScheduler()

async def scheduled_scrape():
    await tender_service.update_cache()

@app.on_event("startup")
async def startup():
    scheduler.add_job(scheduled_scrape, 'cron', hour=0 ,minute=0)
    scheduler.start()



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


