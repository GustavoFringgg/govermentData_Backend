from pydantic import BaseModel
from typing import Optional


#FastAPI 會根據您設定的 BaseModel 自動產生 Swagger (OpenAPI) 文件
#response_model=List[TenderItem]: FastAPI 會根據您設定的 BaseModel 自動產生 Swagger (OpenAPI) 文件
#None = Null


#定義一個class 繼承 baseModel 
#1.檢查資料型別
#2.轉成JSON格式 ** 
#3.自動產生 Swagger (OpenAPI) 文件
class TenderItem(BaseModel):
    id: Optional[int] = None # 項次
    agency_name: Optional[str] = None # 機關名稱
    tender_name: Optional[str] = None # 檔案名稱 (標案名稱)
    tender_mode: Optional[str] = None # 超標方式 (招標方式)
    procurement_nature: Optional[str] = None # 採購性質
    announcement_date: Optional[str] = None # 公告日期
    deadline: Optional[str] = None # 截止投標
    budget: Optional[str] = None # 預算金額
