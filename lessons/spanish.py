import sys
sys.path.append('../')

from lesson import Lesson
from dualingo_logic import run_lesson


class SpanishLesson(Lesson):
    def __init__(self):
        super().__init__()

    @property
    def language(self):
        return 'es'

    @property
    def vocabulary(self):
        return {
            "niño": "boy",
            "niña": "girl",
            "hombre": "man",
            "mujer": "woman",
            "ella": "she",
            "él": "he",
            "yo": "I",
            "tú": "you",
            "nosotros": "we",
            "ellos": "they",
            "soy": "am",
            "eres": "are",
            "es": "is",
            "agua": "water",
            "leche": "milk",
            "pan": "bread",
            "un": "a",
            "una": "a",
        }
    
        

if __name__ == "__main__":
    lesson = SpanishLesson()
    run_lesson("../cookies/yorai.json", lesson)