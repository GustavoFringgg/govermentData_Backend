import requests

url = "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

try:
    print(f"Requesting {url}...")
    response = requests.get(url, headers=headers, timeout=10, verify=False)
    with open("new_url_dump.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved response to new_url_dump.html")
except Exception as e:
    print(f"Error: {e}")
