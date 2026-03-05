from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import TenderItem,TenderCacheResponse
from scraper import Scraper
from shared.cache import cached_data
from datetime import datetime

import logging

router = APIRouter(prefix="/api/tenders", tags=["tenders"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=TenderCacheResponse)
async def get_tenders(tenderName: Optional[str] = None):
    scraper = Scraper(headless=True)
    # 初始化 scraper 建立新的物件 
    # headless=True: 是否以無頭模式運行 程式會在背景執行瀏覽器 不會顯示
    # 爬完資料後關閉瀏覽器
    try:
        result = scraper.scrape_data(keyword=tenderName)
        cached_data["data"] = result
        cached_data["last_updated"] = str(datetime.now())
        return cached_data
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cached",response_model=TenderCacheResponse)
async def get_cached_tenders():
    if not cached_data["data"]:
        return {"message": "No cached data available. Please try again later.","data":[]}
    return cached_data

#不用特別加HTTPException因為get_cached_tenders不會有error需要throw