from pydantic import BaseModel
from typing import Optional

class TenderItem(BaseModel):
    id: Optional[int] = None # 項次
    agency_name: Optional[str] = None # 機關名稱
    tender_name: Optional[str] = None # 檔案名稱 (標案名稱)
    tender_mode: Optional[str] = None # 超標方式 (招標方式)
    procurement_nature: Optional[str] = None # 採購性質
    announcement_date: Optional[str] = None # 公告日期
    deadline: Optional[str] = None # 截止投標
    budget: Optional[str] = None # 預算金額
