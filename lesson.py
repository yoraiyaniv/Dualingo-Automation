from abc import ABC, abstractmethod
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator
import time
import string
import unicodedata
from random import choice

from fill_blank import fill_blank


class Lesson(ABC):
    def __init__(self, driver=None):
        self.start_url = "https://www.duolingo.com/lesson/unit/1/level/1"
        self.translator = Translator()
        if driver is not None:
            self.set_driver(driver)
        self.hearing_keywords = ["hear", "listen", "speak"]
    
    def set_driver(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)    
    
    def skip_challenge(self):
        try:
            time.sleep(1)
            self.driver.find_element(By.CSS_SELECTOR, "button[data-test='player-skip']").click()        
            self.driver.find_element(By.CSS_SELECTOR, "button[data-test='player-next']").click()
        except:
            pass
    
    def do_3_options_challenge(self):
        original_word = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[2]/div")
        original_word = original_word.get_attribute('innerText')

        options = self.driver.find_elements(By.CSS_SELECTOR, "div[data-test='challenge-choice']")
        for option in options:
            span = option.find_element(By.CSS_SELECTOR, "span[data-test='challenge-judge-text']")
            option_text = span.get_attribute('innerText')
            if self._words_match(original_word, option_text):
                option.click()
                return True
        return False
    
    def click_if_available(self, selector):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            return True
        except:
            return False

    def _safe_translate(self, word, src=None, dest='en'):
        try:
            kwargs = {'dest': dest}
            if src:
                kwargs['src'] = src
            result = self.translator.translate(word, **kwargs)
            return (result.text or '').strip() if result else ''
        except Exception:
            return ''

    def _words_match(self, a: str, b: str) -> bool:
        """Returns True if a and b are translations of each other."""
        norm_a, norm_b = self._normalize(a), self._normalize(b)
        if norm_a == norm_b:
            return True
        all_a = self._translate_all(a, src=self.language, dest='en') | self._translate_all(a, src='en', dest=self.language)
        all_b = self._translate_all(b, src=self.language, dest='en') | self._translate_all(b, src='en', dest=self.language)
        return norm_b in all_a or norm_a in all_b

    def _translate_all(self, word, src=None, dest='en'):
        """Returns a set of all possible normalized translations including alternatives."""
        translations = self._vocab_lookup(word)
        try:
            kwargs = {'dest': dest}
            if src:
                kwargs['src'] = src
            result = self.translator.translate(word, **kwargs)
            if not result:
                return translations
            if result.text:
                translations.add(self._normalize(result.text.strip()))
            for group in (result.extra_data.get('all-translations') or []):
                if isinstance(group, list) and len(group) > 1 and isinstance(group[1], list):
                    for alt in group[1]:
                        if isinstance(alt, str):
                            translations.add(self._normalize(alt))
        except Exception:
            pass
        return translations

    def translate(self, word):
        result = self._safe_translate(word, dest=self.language)
        if not result or self._normalize(result) == self._normalize(word):
            result = self._safe_translate(word, dest='en')
        return result or word

    
    @staticmethod
    def _normalize(text):
        return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii').lower()

    def arrange_tiles(self, tiles: list, sentence: str):
        sentence = ''.join(ch for ch in sentence if ch not in string.punctuation)
        sentence_tokens = sentence.split()

        tiles_pool = []
        for tile in tiles:
            tile_text = tile.get_attribute('innerText').strip()
            if tile_text == "'re":
                tile_text = "are"
            tile_text = ''.join(ch for ch in tile_text if ch not in string.punctuation)
            tiles_pool.append((tile_text, tile))

        arranged = []
        used = [False] * len(tiles_pool)
        for token in sentence_tokens:
            norm_token = self._normalize(token)
            found = False

            # First pass: exact match
            for i, (tile_text, tile) in enumerate(tiles_pool):
                if not used[i] and self._normalize(tile_text) == norm_token:
                    arranged.append(tile)
                    used[i] = True
                    found = True
                    break

            # Second pass: synonym match
            if not found:
                synonyms = (self._translate_all(token, src=self.language, dest='en') |
                            self._translate_all(token, src='en', dest=self.language))
                for i, (tile_text, tile) in enumerate(tiles_pool):
                    if not used[i] and self._normalize(tile_text) in synonyms:
                        arranged.append(tile)
                        used[i] = True
                        found = True
                        break

            if not found:
                print(f"Token '{token}' not found in tiles")
                return []

        return arranged

    def do_tiles_challenge(self):
        sentence_el = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div/div[2]/div")
        sentence = sentence_el.get_attribute('innerText').strip()

        tiles = self.driver.find_elements(By.CSS_SELECTOR, "button[data-test*='challenge-tap-token']")

        # Try each possible translation direction until tiles match
        seen = set()
        candidates = []
        words = ''.join(ch for ch in sentence if ch not in string.punctuation).split()
        word_by_word_to_en = ' '.join(self._safe_translate(w, src=self.language, dest='en') or w for w in words)
        word_by_word_to_tl = ' '.join(self._safe_translate(w, src='en', dest=self.language) or w for w in words)

        for text in [
            sentence,
            self._safe_translate(sentence, dest='en'),
            self._safe_translate(sentence, src=self.language, dest='en'),
            self._safe_translate(sentence, src='en', dest=self.language),
            word_by_word_to_en,
            word_by_word_to_tl,
        ]:
            if text and text not in seen:
                seen.add(text)
                candidates.append(text)

        arranged_tiles = []
        for candidate in candidates:
            arranged_tiles = self.arrange_tiles(tiles, candidate)
            if len(arranged_tiles) > 0:
                break

        if len(arranged_tiles) == 0:
            print("Could not arrange tiles, skipping challenge")
            return False
        
        for tile in arranged_tiles:
            tile.click()
            time.sleep(0.5)
        return True

    def do_matching_challenge(self):
        tap_tokens = self.driver.find_elements(By.CSS_SELECTOR, "button[data-test*='challenge-tap-token']")
        num_per_side = len(tap_tokens) // 2
        left_tokens = {elm.find_element(By.CSS_SELECTOR, "span[data-test='challenge-tap-token-text']").get_attribute('innerText'): elm for elm in tap_tokens[:num_per_side]}
        right_tokens = {elm.find_element(By.CSS_SELECTOR, "span[data-test='challenge-tap-token-text']").get_attribute('innerText'): elm for elm in tap_tokens[num_per_side:]}
        for left_text, left_elm in left_tokens.items():
            for right_text, right_elm in right_tokens.items():
                if self._words_match(left_text, right_text):
                    left_elm.click()
                    time.sleep(0.5)
                    right_elm.click()
                    time.sleep(0.5)
                    break
        return True
    
    def do_complete_chat(self):
        choice(self.driver.find_elements(By.CSS_SELECTOR, "button[data-test='challenge-choice']")).click()
        time.sleep(0.5)
        return True

    def do_fill_in_the_blank_challenge(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test$='challenge-tap-token']")))
        tiles = self.driver.find_elements(By.CSS_SELECTOR, "button[data-test$='challenge-tap-token']")
        tiles = tiles[(len(tiles)//2):]
        choice(tiles).click()
        time.sleep(0.5)
        return True

    def do_challenge(self):
        time.sleep(2)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-test='challenge-header']")))
        code = None
        if len(self.driver.find_elements(By.CSS_SELECTOR, "div[data-test='challenge-choice']")) == 3:
            code = self.do_3_options_challenge()
        elif any(k in str(self.driver.find_element(By.CSS_SELECTOR, "h1[data-test='challenge-header']").get_attribute('innerText')).lower() for k in self.hearing_keywords):
            code = False
        elif "matching pairs" in str(self.driver.find_element(By.CSS_SELECTOR, "h1[data-test='challenge-header']").get_attribute('innerText')):
            code = self.do_matching_challenge()
        elif "the chat" in str(self.driver.find_element(By.CSS_SELECTOR, "h1[data-test='challenge-header']").get_attribute('innerText')):
            code = self.do_complete_chat()
        elif "in the blank" in str(self.driver.find_element(By.CSS_SELECTOR, "h1[data-test='challenge-header']").get_attribute('innerText')):
            code = self.do_fill_in_the_blank_challenge()
        elif len(self.driver.find_elements(By.CSS_SELECTOR, "button[data-test*='challenge-tap-token']")) > 0:
            code = self.do_tiles_challenge()
        elif not self.driver.find_element(By.CSS_SELECTOR, "button[data-test='player-next']").get_attribute("aria-disabled"):
            code = True
        else:
            return False
        self.click_if_available("button[data-test='player-next']")
        self.click_if_available("button[data-test='player-next']")
        return code
    
    def do(self):
        skips = 10

        self.driver.get("https://www.duolingo.com/lesson/unit/1/level/1")

        while skips > 0:
            try:
                result = self.do_challenge()
            except Exception as e:
                print(f"Error during challenge: {e}")
                input("Press Enter to continue...")
                result = False
            if result is False:
                self.skip_challenge()
                skips -= 1

    @property
    @abstractmethod
    def vocabulary(self) -> dict:
        pass

    def _vocab_lookup(self, word: str) -> set:
        """Returns all known translations of a word from the vocabulary."""
        norm = self._normalize(word)
        results = set()
        for k, v in self.vocabulary.items():
            if self._normalize(k) == norm:
                results.add(self._normalize(v))
            if self._normalize(v) == norm:
                results.add(self._normalize(k))
        return results

    @property
    @abstractmethod
    def language(self):
        pass
    

if __name__ == "__main__":
    class DummyLesson(Lesson):
        @property
        def language(self):
            return "es"

    # Example usage
    from selenium import webdriver
    driver = webdriver.Chrome()

    lesson = DummyLesson(driver)
    print(lesson.translate("hello"))