from fastapi.testclient import TestClient
from main import app
from shared.cache import cached_data  # ← import 同一個 cache 物件
from models import TenderItem

client = TestClient(app)

def test_cache_empty():
    cached_data["data"] = []
    cached_data["last_updated"] = None

    response = client.get("/api/tenders/cached")
    assert response.status_code == 200
    assert response.json()["data"] == []

def test_cache_with_data():
    # 1. 準備測試資料
    test_item = TenderItem( # 建立一個 TenderItem 物件
        id=1,
        agency_name="測試機關",
        tender_name="測試標案",
        tender_mode="公開招標",
        procurement_nature="工程",
        announcement_date="2023-01-01",
        deadline="2023-01-10",
        budget="100000"
    )
    cached_data["data"] = [test_item]
    cached_data["last_updated"] = "2023-01-01T00:00:00"

    response = client.get("/api/tenders/cached")

    assert response.status_code == 200
    result = response.json()

    assert len(result["data"]) == 1
    assert result["data"][0]["tender_name"] == "測試標案"
    assert result["last_updated"] is not None
