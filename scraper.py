from selenium import webdriver # 操控瀏覽器的入口
from selenium.webdriver.chrome.service import Service #管理Chrome瀏覽器的服務
from selenium.webdriver.common.by import By #定「怎麼找」網頁元素  By.ID (找 ID), By.CLASS_NAME (找類別), By.XPATH (用路徑找)

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 兩個一組，專門處理 「動態等待」
# WebDriverWait：設定一個最長等待時間（例如 10 秒）
# expected_conditions：設定「要等什麼條件」例如：直到元素出現、直到按鈕可點擊

import os # 用來偵測作業系統環境，決定 Chrome 路徑
from selenium.webdriver.chrome.options import Options #設定 Chrome 瀏覽器的啟動參數
from bs4 import BeautifulSoup
#Selenium 負責「操作」瀏覽器（點擊、輸入、等待）
#BeautifulSoup 負責「解析」網頁原始碼（抓取文字、整理資料）

import time #Python 內建的時間模組 time.sleep(3)（強制休息 3 秒），避免爬太快被網站封鎖 IP，或者單純等待網頁動畫跑完
import logging
from typing import List, Dict #型別提示 (Type Hinting)。讓程式碼更易讀，告訴開發者這個變數應該是 List 還是 Dict

from models import TenderItem
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) #讓Log印出來時會掛上這個檔案的名字，方便辨識 
# type logger =>  <class 'logging.Logger'>
#logger.debug("詳細除錯資訊")
#logger.info("一般資訊")
#logger.warning("警告訊息")
#logger.error("錯誤訊息")
#logger.critical("嚴重錯誤")



class Scraper:
    #init: 狀態設定
    #setup_driver: 專注在環境準備
    #scrape_data: 專注在業務邏輯
    def __init__(self, headless: bool = True): #初始化設定（建構子 Constructor）
        self.headless = headless #是否以無頭模式運行 程式會在背景執行瀏覽器 不會顯示
        self.driver = None #先把瀏覽器設為None，初始位尚未開啟
        #創建一個新的物件實例 (s = Scraper()) 時，Python 會自動去呼叫這個 init 方法

    def setup_driver(self): #啟動瀏覽器
        chrome_options = Options() 
        if self.headless:
            chrome_options.add_argument("--headless") # 瀏覽器會在背景執行，不顯示視窗（無頭模式）
        chrome_options.add_argument("--no-sandbox") # 停用沙盒安全機制。在 Linux / Docker 環境中必須加，否則 Chrome 可能無法啟動
        chrome_options.add_argument("--disable-dev-shm-usage") #避免 Chrome 在記憶體不足時崩潰，改為使用 /tmp 暫存
        chrome_options.add_argument("--window-size=1920,1080") #設定瀏覽器視窗大小為 1920×1080。headless 模式沒有真實視窗，需要手動指定
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36") # 偽裝成一般使用者的瀏覽器資訊
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") # 隱藏 Chrome 被 Selenium 控制的特徵（正常瀏覽器不會有 navigator.webdriver = true），反爬蟲偵測用
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #移除 Chrome 頂部的「Chrome 正受到自動化測試軟體控制」警示列，讓行為更接近正常使用者。
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # 停用 Chrome 自動化擴充套件，進一步降低被識別為機器人的機率。

        # 根據環境決定 Chrome/ChromeDriver 路徑
        # 在 Docker (Render) 上使用系統安裝的 chromium
        # 在本機 Windows 開發時，讓 Selenium 自動尋找 Chrome
        if os.path.exists("/usr/bin/chromium"):  # Docker / Linux 環境（Render）
            chrome_options.binary_location = "/usr/bin/chromium"
            self.driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)
        else:  # 本機 Windows 開發環境，使用 webdriver-manager 自動管理
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_data(self, keyword: Optional[str] = None) -> List[TenderItem]:  #類TS 回傳顯示格式為 List[TenderItem]
        if not self.driver:
            self.setup_driver()

        base_url = "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic"
        results = []
        page = 1
        max_pages = 30 

        try:
            while page <= max_pages:

                url = f"{base_url}?d-49738-p={page}"
                
                if keyword:
                    url += f"&tenderName={keyword}"

                logger.info(f"Navigating to page {page}: {url}")

                self.driver.get(url) #開啟真實瀏覽器

                wait = WebDriverWait(self.driver, 10) #設定等待時間(顯性等待)
                try:
                    # 意思：「等到 id='tpam' 的 table 出現，才繼續執行下一行」
                    # 如果 10 秒內沒出現 → 拋出 TimeoutException → 被 except 捕捉 → break
                    # 這裡使用selenium找元素，是因為前端如果是JS渲染，就須依賴此查找DOM
                    wait.until(EC.presence_of_element_located((By.ID, "tpam")))
                except:
                    logger.warning(f"Timeout waiting for table on page {page}. Stopping.")
                    break
                
                #time.sleep(1) #保護機制 (暫時取消 加快爬蟲速度)

                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                #self.driver.page_source 完整 HTML 字串

                target_table = soup.find('table', id='tpam')
                
                if not target_table: #如果沒有找到table 就回傳None
                    logger.warning(f"No table found on page {page}. Stopping.")
                    break

                # table => tbody => tr
                rows = target_table.find('tbody').find_all('tr')
                if not rows: #如果沒有找到row 就回傳None
                    logger.warning(f"No rows found on page {page}. Stopping.")
                    break
                    
                logger.info(f"Found {len(rows)} rows on page {page}.")
                
                current_page_count = 0 #初始化解析幾筆資料

                import re # 引入正規表達式模組

                for row in rows:
                    cols = row.find_all('td') #return list 
                    #cols[0]  # 編號
                    #cols[1]  # 機關名稱
                    #cols[2]  # 標案名稱

                    if len(cols) < 9: # 少於9欄資料 就跳過
                        continue 
  
                    # 1. 取得純文字
                    # 2. 使用正規表達式尋找連續數字
                    # 3. 轉換成整數
                    id_text_full = cols[0].get_text(strip=True) # BeautifulSoup 的方法，用來取得標籤內的純文字
                    id_match = re.search(r'\d+', id_text_full) 
                    # r'\d+' 是一個正規表達式，意思是「尋找一個或多個連續的數字」r = raw string 加入 r 不會被當跳脫字元
                    item_id = int(id_match.group(0)) if id_match else None
                    # group(0) 找到的第一個符合條件的字串
                    # 有找到 → 轉成 int，例如 123 沒找到 → 設為 None

                    # 將預算金額 使用 replace() 移除逗號
                    budget_raw = cols[8].get_text(strip=True).replace(',', '')

                    item = TenderItem(
                        id=item_id,
                        agency_name=cols[1].get_text(strip=True),
                        tender_name=cols[2].get_text(strip=True),  #如果只想要標案名稱=> cols[2].find('a').get_text(strip=True)
                        tender_mode=cols[4].get_text(strip=True),
                        procurement_nature=cols[5].get_text(strip=True),
                        announcement_date=cols[6].get_text(strip=True),
                        deadline=cols[7].get_text(strip=True),
                        budget=budget_raw
                    )
                    results.append(item) # 組合 json 格式
                    current_page_count += 1
                
                if current_page_count == 0: #當沒有資料可以爬，就 break 進 logger.info
                    logger.info("No valid items parsed on this page. Stopping.")
                    break
                    
                page += 1
                
            logger.info(f"Total scraped {len(results)} items across {page-1} pages.")

        except Exception as e: 
            logger.error(f"Error during scraping: {e}") # 記錄錯誤訊息
            if self.driver:
                self.driver.save_screenshot("debug_error.png")
            raise e # 把錯誤繼續往上拋（讓 main.py 的 except 接到）
        finally:
            if self.driver:
                self.driver.quit()  # 關閉瀏覽器
                self.driver = None  # 清除 driver 參考

        return results


if __name__ == "__main__":
    # Test run
    s = Scraper(headless=False) # Try headed locally if headless fails
    try:
        data = s.scrape_data()
        print(f"Got {len(data)} records.")
    except Exception as e:
        print(f"Failed: {e}")
