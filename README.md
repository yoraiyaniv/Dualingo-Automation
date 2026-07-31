# Duolingo Automation

A browser-automation bot that logs into Duolingo and works through a lesson on its own — detecting what kind of challenge is on screen (multiple choice, tile-arrangement translation, matching pairs, fill-in-the-blank, chat completion) and solving each one with a mix of translation lookups and a purpose-built vocabulary dictionary, rather than hardcoded answers.

> **Status:** working prototype for the core lesson types. An earlier version of this repo committed a live Duolingo session cookie (including an auth token) — that's since been removed, git history was cleaned up, and `cookies/` is now git-ignored, with `extract_cookies.py` provided to regenerate a session locally instead.

---

## How it works

1. **`extract_cookies.py`** opens a real Chrome profile, waits for you to log in by hand, and saves the resulting session cookies to a JSON file — a one-time setup step rather than storing a password anywhere.
2. **`dualingo_logic.py`** launches a Selenium-driven Chrome session, loads the saved cookies to skip login, and hands off to a `Lesson`.
3. **`lesson.py`** is the core engine: an abstract `Lesson` base class that inspects the challenge header and DOM structure on screen to figure out *which kind* of Duolingo exercise it's looking at, then dispatches to the matching solver:
   - **Multiple choice** — compares the prompt word against each option using bidirectional translation matching
   - **Tile/sentence-building challenges** — translates the target sentence multiple ways (word-by-word and whole-sentence, in both directions) and greedily matches tiles against whichever translation actually lines up with the tiles on screen
   - **Matching pairs** — pairs left/right tokens by testing whether each pair is a translation of the other
   - **Chat completion** — currently a random choice among valid options
   - **Fill-in-the-blank** — currently picks randomly (see Roadmap — there's an unused masked-language-model solver already written for this)
4. Every language gets its own subclass (`lessons/spanish.py` is the example) supplying a hand-curated vocabulary dictionary that's checked *before* falling back to a live translation API call — faster and more reliable for common words.

---

## Skills demonstrated

**Browser automation done properly**
- Selenium driving a real Chrome session against a live, unpredictable production website (not a test fixture) — waiting for elements, handling multiple DOM layouts for different challenge types, and recovering gracefully (skip-and-continue) when a challenge type can't be solved
- Session reuse via cookie injection instead of scripting the login form, avoiding CAPTCHAs/bot-detection triggered by automated logins

**Genuine problem-specific algorithm design**
- The tile-arrangement solver isn't a lookup table — it generates multiple candidate translations of a target sentence (direct, word-by-word, both language directions) and tries each against the available tiles until one produces a full match, then does two-pass matching (exact text, then synonym-via-translation) to place each tile correctly
- A vocabulary-first, translation-API-fallback design for word matching — checking a fast local dictionary before making a network call, and normalizing text (accent-stripping, casing) so "niño" and "nino" compare correctly

**Object-oriented design for extensibility**
- Abstract base class (`Lesson`) separates the *generic* challenge-solving logic (shared across all languages) from the *language-specific* data (vocabulary, language code), so adding a new language is a ~20-line subclass, not new logic

**Applied ML, already scaffolded**
- `fill_blank.py` uses a real masked-language model (`xlm-roberta-base` via Hugging Face `transformers`) to score candidate words against a masked sentence by their predicted-token logits — a legitimate NLP technique, ready to be wired into the fill-in-the-blank challenge once connected

**Deployment**
- Dockerfile that installs headless Chrome and its full dependency chain from scratch (not relying on a pre-built Selenium image), with timezone configuration for scheduled/cron-style runs

---

## Tech stack

| Layer | Tools |
|---|---|
| Browser automation | Selenium, Chrome |
| Translation | googletrans |
| NLP / ML | Hugging Face `transformers` (xlm-roberta-base), PyTorch |
| Deployment | Docker |

---

## Getting started

```bash
pip install selenium webdriver-manager googletrans transformers torch

# One-time: log in and capture a session
python extract_cookies.py
mkdir -p cookies && mv duolingo_cookies.json cookies/yorai.json

# Run a lesson
python lessons/spanish.py
```

Or via Docker:
```bash
docker build -t duolingo-bot .
docker run duolingo-bot
```

---

## Roadmap / known limitations

- **The `main.py` entry point is out of sync with the rest of the code**: it calls `run_lesson("cookies/yorai.json", None)`, passing `None` where a `Lesson` instance is expected — this will crash immediately (`AttributeError` on `None.set_driver`). `lessons/spanish.py` is the actual working entry point right now; `main.py` needs to construct and pass a real lesson object.
- **Fill-in-the-blank and chat-completion challenges are still random guesses**: the masked-language-model solver in `fill_blank.py` exists and works standalone but isn't called from `lesson.py`'s `do_fill_in_the_blank_challenge` yet — there's a stray file in the repo root literally named `TODO: Implement fill the blank challenge` marking this as unfinished.
- **Hearing/listening challenges aren't handled** — the code explicitly detects them and returns `False` (skip) rather than attempting a solution.
- **Only one language is implemented** (`lessons/spanish.py`); the abstraction is there for more, but no others are written yet.
- **No tests** — correctness has been validated by running it against the live site and watching what happens, which is reasonable for browser automation but leaves regressions easy to miss if Duolingo changes its DOM.
- **Worth being aware of**: automating a gamified learning app like this is usually against the platform's terms of service — fine for a personal side project, but worth a mental note if this ever runs anywhere more visible than a personal machine.

The interesting engineering here — multi-strategy translation matching, DOM-based challenge-type detection, and a real (if not-yet-wired-in) MLM-based solver — already works for the core challenge types. The gaps above are specific and well-scoped, not structural problems.
