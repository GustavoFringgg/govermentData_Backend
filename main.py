from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import TenderItem
from scraper import Scraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Government Tender Scraper API")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:5173", # Common Vue/Vite port
    "*" # Allow all for development convenience
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper
# Note: In a production environment, you might want to use a background task
# or a singleton pattern more carefully. For now, we instantiate on request
# or keep a global instance if we want to reuse the driver (though reuse can be tricky with state).
# For simplicity and robustness, we'll instantiate per request or use a simple cached approach.
# Since scraping takes time, a synchronous endpoint will block. 
# We should probably run this asynchronously or just accept the delay for now as per user request.

@app.get("/api/tenders", response_model=List[TenderItem])
async def get_tenders(tenderName: str = None):
    """
    Scrapes the government website and returns tender data.
    This operation is time-consuming.
    """
    scraper = Scraper(headless=True)
    try:
        data = scraper.scrape_data(keyword=tenderName)
        return data
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)


