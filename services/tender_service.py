import logging
from datetime import datetime
from scraper import Scraper
from shared.cache import cached_data

logger = logging.getLogger(__name__)


async def update_cache():
    logger.info("Starting scheduled scrape...")
    scraper = Scraper(headless=True)
    try:
        result = scraper.scrape_data()
        cached_data["data"] = result
        cached_data["last_updated"] = str(datetime.now())
        logger.info(f"Scraped {len(result)} items.")
    except Exception as e:
        logger.error(f"Scheduled scrape failed: {e}")
