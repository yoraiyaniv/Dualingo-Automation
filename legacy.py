from dotenv import load_dotenv
load_dotenv()

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator
import asyncio
import time


EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
PROFILE_PATH = r"Profile 1"
DICTIONARY = {
    "water": "agua",
    "apple": "manzana",
    "bread": "pan",
    "milk": "leche",
    "girl": "niña"
}



            
def arrange_tiles(tiles: list, sentence: str):
    arranged = []
    max_tries = len(tiles) * 2  # Prevent infinite loops
    while len(sentence) > 0 and len(tiles) > 0 and max_tries > 0:
        for tile in tiles:
            tile_text = tile.get_attribute('innerText')
            if tile_text == "'re":
                tile_text = "are"
            if sentence.startswith(tile_text):
                arranged.append(tile)
                sentence = sentence[len(tile_text):].lstrip()  # Remove the matched part and any leading whitespace
                tiles.remove(tile)
                break
        max_tries -= 1
    return arranged

def is_this_spanish(sentence):
    # call google translate api to detect language
    translator = Translator()
    try:
        detected = asyncio.run(translator.detect(sentence))
        return detected.lang == 'es'
    except:
        return False

def do_tiles_challenge(driver):
    sentence = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[2]/div")
    sentence = sentence.get_attribute('innerText')
    print(f"sentence: {sentence}")
    
    tiles = driver.find_elements(By.CSS_SELECTOR, "button[data-test*='challenge-tap-token']")
    print(f"Found {len(tiles)} tiles")
    
    translator = Translator()
    if is_this_spanish(sentence):
        translated = asyncio.run(translator.translate(sentence, src='es', dest='en'))
        translated = translated.text
        print(f"Translated sentence: {translated}")
    else:
        translated = sentence
    
    arranged_tiles = arrange_tiles(tiles, translated)
    print(f"Arranged {len(arranged_tiles)} tiles")
    print(f"Arranged tiles text: {[tile.get_attribute('innerText') for tile in arranged_tiles]}")
    

def do_lesson(driver):
    wait = WebDriverWait(driver, 20)
    
    driver.get_print("https://www.duolingo.com/lesson/unit/1/level/1")
    
    while True:
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[2]/div")))
        if len(driver.find_elements(By.CSS_SELECTOR, "div[data-test='challenge-choice']")) == 3:
            do_3_options_challenge(driver)
            time.sleep(2)
        elif len(driver.find_elements(By.CSS_SELECTOR, "button[data-test*='challenge-tap-token']")) > 0:
            do_tiles_challenge(driver)
            time.sleep(2)
        else:
            print("Challenge type not supported yet")
            skip_challenge(driver)
            print("Skipped unsupported challenge")

def click_if_available(selector, wait):
    try:
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        element.click_print()
        return True
    except:
        return False

def do_story_challenge(driver):
    wait = WebDriverWait(driver, 10)
    
    driver.get_print("https://www.duolingo.com/lesson/unit/4/level/2")
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test='story-start']")))
    click_if_available("button[data-test='story-start']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test='stories-choice']")))
    try:
        for i in range(2):
            li = driver.find_elements(By.CSS_SELECTOR, "._25kWt")[i]
            if "Yes" in li.get_attribute('innerText'):
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='stories-choice']")))
                li.find_element(By.CSS_SELECTOR, "button").click_print()
                break
    except:
        pass
    
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    click_if_available("button[data-test='Necesito-challenge-tap-token']", wait)
    click_if_available("button[data-test='las llaves-challenge-tap-token']", wait)
    click_if_available("button[data-test='de-challenge-tap-token']", wait)
    click_if_available("button[data-test='mi-challenge-tap-token']", wait)
    click_if_available("button[data-test='carro-challenge-tap-token']", wait)
    
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    click_if_available("button[data-test='cansada-challenge-tap-token']", wait)
    
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test='stories-choice']")))
    time.sleep(2)
    for i in range(3):
        li = driver.find_elements(By.CSS_SELECTOR, "._25kWt")[i]
        if "looking" in li.get_attribute('innerText'):
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='stories-choice']")))
            li.find_element(By.CSS_SELECTOR, "button").click_print()
            break

    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test='stories-choice']")))
    time.sleep(2)
    for i in range(3):
        li = driver.find_elements(By.CSS_SELECTOR, "._25kWt")[i]
        if "salt" in li.get_attribute('innerText'):
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='stories-choice']")))
            li.find_element(By.CSS_SELECTOR, "button").click_print()
            break
        
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    text = [elm.get_attribute('innerText') for elm in driver.find_elements(By.CSS_SELECTOR, "span[data-test='challenge-tap-token-text']")[:5]]
    
    actions = {
        "please": ["please-challenge-tap-token", "favor-challenge-tap-token por"],
        "love": ["love-challenge-tap-token", "amor-challenge-tap-token"],
        "here": ["here-challenge-tap-token", "aquí-challenge-tap-token"],
        "sugar": ["sugar-challenge-tap-token", "azúcar-challenge-tap-token"],
        "tired": ["tired-challenge-tap-token", "cansada-challenge-tap-token"],
        "keys": ["keys-challenge-tap-token", "llaves-challenge-tap-token"],
        "coffee": ["coffee-challenge-tap-token", "café-challenge-tap-token"],
        "salt": ["salt-challenge-tap-token", "sal-challenge-tap-token"],
        "I need": ["I need-challenge-tap-token", "necesito-challenge-tap-token"],
        "good morning": ["good morning-challenge-tap-token", "buenos días-challenge-tap-token"],
        "table": ["table-challenge-tap-token", "mesa-challenge-tap-token"],
        "work": ["work-challenge-tap-token", "trabajo-challenge-tap-token"],
        "car": ["car-challenge-tap-token", "carro-challenge-tap-token"],
        "sorry": ["sorry-challenge-tap-token", "perdón-challenge-tap-token"],
        "you want": ["want-challenge-tap-token you", "quieres-challenge-tap-token"],
    }
    
    for word in text:
        if word in actions:
            click_if_available(f"button[data-test='{actions[word][0]}']", wait)
            click_if_available(f"button[data-test='{actions[word][1]}']", wait)
    
    click_if_available("button[data-test='stories-player-continue']", wait)
    
    time.sleep(10)
    
    if not wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='session-complete-slide']"))):
        print("Session complete slide not found.")
        return
    
    print("Session complete slide found.")


def run_lesson(driver):
    opts = Options()
    opts.add_argument(f"--user-data-dir={PROFILE_PATH}")
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=opts)
    driver.get_print = lambda x: (print(f"Navigating to: {x}"), driver.get(x))[1]
    WebElement.click_print = lambda self: (print(f"Clicking on element"), self.click())[1]  
    try:
        do_lesson(driver)
    except Exception as e:
        print(f"An error occurred: {e}")
    driver.quit()
    

if __name__ == "__main__":
    
    opts = Options()
    opts.add_argument(f"--user-data-dir={PROFILE_PATH}")
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=opts)
    driver.get_print = lambda x: (print(f"Navigating to: {x}"), driver.get(x))[1]
    WebElement.click_print = lambda self: (print(f"Clicking on element"), self.click())[1]
    
    try:
        do_story_challenge(driver)
    except Exception as e:
        print(f"An error occurred: {e}")
    
    driver.quit()   
    exit()