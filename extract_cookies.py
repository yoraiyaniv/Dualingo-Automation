from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle
import json

opts = Options()
opts.add_argument("--user-data-dir=profiles/Profile 1")  # Your local profile

driver = webdriver.Chrome(options=opts)
driver.get("https://www.duolingo.com")

input("Press Enter after you're logged in...")

# Save cookies
cookies = driver.get_cookies()
with open('duolingo_cookies.json', 'w') as f:
    json.dump(cookies, f)

print("Cookies saved to duolingo_cookies.json")
driver.quit()