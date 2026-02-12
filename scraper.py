from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict
from models import TenderItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # Anti-detection headers
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_data(self, keyword: str = None) -> List[TenderItem]:
        if not self.driver:
            self.setup_driver()

        base_url = "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic"
        results = []
        page = 1
        max_pages = 30 # User mentioned ~8 pages, but 1100 records / 50 per page = 22 pages. Set 30 safe limit.

        try:
            while page <= max_pages:
                # Construct URL with pagination
                # d-49738-p is the page parameter based on the HTML analysis
                url = f"{base_url}?d-49738-p={page}"
                
                if keyword:
                    url += f"&tenderName={keyword}" # Note: This param name is a guess, might need adjustment if search doesn't work by URL

                logger.info(f"Navigating to page {page}: {url}")
                self.driver.get(url)

                wait = WebDriverWait(self.driver, 10)
                try:
                    # Wait for table
                    wait.until(EC.presence_of_element_located((By.ID, "tpam")))
                except:
                    logger.warning(f"Timeout waiting for table on page {page}. Stopping.")
                    break
                
                time.sleep(1) # Be nice to the server

                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                target_table = soup.find('table', id='tpam')
                
                if not target_table:
                    logger.warning(f"No table found on page {page}. Stopping.")
                    break

                rows = target_table.find('tbody').find_all('tr')
                if not rows:
                    logger.info(f"No rows found on page {page}. Stopping.")
                    break
                    
                logger.info(f"Found {len(rows)} rows on page {page}.")
                
                current_page_count = 0

                import re

                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 9:
                        continue 
                    
                    # ID Extraction: Handle <span class="red">!</span> or other noise
                    # Just grab the first sequence of digits
                    id_text_full = cols[0].get_text(strip=True)
                    id_match = re.search(r'\d+', id_text_full)
                    item_id = int(id_match.group(0)) if id_match else None
                    
                    # Tender Name Extraction
                    tender_name_raw = None
                    name_cell = cols[2]
                    name_match = re.search(r'pageCode2Img\("(.*?)"\)', str(name_cell))
                    if name_match:
                        tender_name_raw = name_match.group(1)
                    else:
                        tender_name_raw = name_cell.get_text(strip=True)

                    # Budget
                    budget_raw = cols[8].get_text(strip=True).replace(',', '')

                    item = TenderItem(
                        id=item_id,
                        agency_name=cols[1].get_text(strip=True),
                        tender_name=tender_name_raw,
                        tender_mode=cols[4].get_text(strip=True),
                        procurement_nature=cols[5].get_text(strip=True),
                        announcement_date=cols[6].get_text(strip=True),
                        deadline=cols[7].get_text(strip=True),
                        budget=budget_raw
                    )
                    results.append(item)
                    current_page_count += 1
                
                if current_page_count == 0:
                    logger.info("No valid items parsed on this page. Stopping.")
                    break
                    
                page += 1
                
            logger.info(f"Total scraped {len(results)} items across {page-1} pages.")

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            if self.driver:
                self.driver.save_screenshot("debug_error.png")
            raise e
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

        return results



if __name__ == "__main__":
    # Test run
    s = Scraper(headless=False) # Try headed locally if headless fails
    try:
        data = s.scrape_data()
        print(f"Got {len(data)} records.")
        if data:
            print(data[0])
    except Exception as e:
        print(f"Failed: {e}")
