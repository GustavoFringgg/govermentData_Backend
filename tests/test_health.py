from fastapi.testclient import TestClient
from main import app

client = TestClient(app) # 模擬一個 HTTP client，不需要真的跑 server

def test_health_check():
    response = client.get('/health/')
    assert response.status_code == 200  # like Jest expect(response.status).toBe(200)
    assert response.json() == {"status": "ok"} # like Jest expect(response.json()).toEqual({status: "ok"})

