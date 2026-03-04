from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import TenderItem,TenderCacheResponse
from scraper import Scraper
from shared.cache import cached_data
import logging

router = APIRouter(prefix="/api/tenders", tags=["tenders"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[TenderItem])
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


@router.get("/cached",response_model=TenderCacheResponse)
async def get_cached_tenders():
    if not cached_data["data"]:
        return {"message": "No cached data available. Please try again later.","data":[]}
    return cached_data