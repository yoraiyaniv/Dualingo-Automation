from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

from lesson import Lesson

def load_cookies(driver, cookie_file):
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
        
        # Navigate to domain first
        driver.get("https://www.duolingo.com")
        
        # Add cookies
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
        
        # Refresh to apply cookies
        driver.get("https://www.duolingo.com")
        print("Cookies loaded successfully!")
        return True
    return False

def click_if_available(selector, wait):
    try:
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        element.click()
        return True
    except:
        return False

def run_lesson(cookies_path, lesson: Lesson):    
    opts = Options()
    driver = webdriver.Chrome(options=opts)
    driver_reference = driver  # Update the reference to the driver in the calling scope
    driver.get_print = lambda x: (print(f"Navigating to: {x}"), driver.get(x))[1]

    try:
        if not load_cookies(driver, cookies_path):
            print("Warning: No cookies found, may need to login")
        
        lesson.set_driver(driver)
        lesson.do()
        
    except Exception as e:
        print(f"An error occurred: {e}")
    input("Press Enter to exit...")
    driver.quit()

if __name__ == "__main__": 
    global driver_reference
    
    driver_reference = None
        
    try:
        run_lesson("cookies/yorai.json")
    except Exception as e:
        print(f"An error occurred while running the lesson: {e}")
        if driver_reference:
            driver_reference.quit()