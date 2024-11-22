from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

url = 'https://dubaicityofgold.com/'

driver.get(url)

time.sleep(5)

gold_prices = driver.find_elements(By.CSS_SELECTOR, "ul.goldtable li")

prices = {}
for price in gold_prices:
    text = price.text.strip()
    if text:
        gold_type, price_value = text.split(" - AED ")
        prices[gold_type.strip()] = price_value.strip()

driver.quit()
for gold_type, price in prices.items():
    print(f"{gold_type}: AED {price}")
