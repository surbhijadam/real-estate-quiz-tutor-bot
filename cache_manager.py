"""
cache_manager.py
----------------
Handles persistent caching of generated questions and evaluations
to minimize API calls and handle quota limits gracefully.
"""

import json
import os
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
import google.api_core.exceptions as api_exceptions


CACHE_DIR = Path(__file__).parent / "cache"
QUESTIONS_CACHE = CACHE_DIR / "questions.json"
ANSWERS_CACHE = CACHE_DIR / "answers.json"


def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(exist_ok=True)


def load_json_cache(cache_file: Path) -> Dict:
    """Load cache from JSON file."""
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_json_cache(cache_file: Path, data: Dict):
    """Save cache to JSON file."""
    ensure_cache_dir()
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)


def get_cache_key(topic: str, difficulty: str = "intermediate") -> str:
    """Generate a cache key for topic+difficulty."""
    key_str = f"{topic}_{difficulty}".lower().replace(" ", "_")
    return hashlib.md5(key_str.encode()).hexdigest()[:12]


def get_cached_question(topic: str, difficulty: str = "intermediate") -> Optional[Dict]:
    """Retrieve a cached question if available."""
    cache = load_json_cache(QUESTIONS_CACHE)
    key = get_cache_key(topic, difficulty)
    if key in cache:
        return cache[key]
    return None


def cache_question(topic: str, difficulty: str, question_data: Dict):
    """Store a generated question in cache."""
    ensure_cache_dir()
    cache = load_json_cache(QUESTIONS_CACHE)
    key = get_cache_key(topic, difficulty)
    cache[key] = question_data
    save_json_cache(QUESTIONS_CACHE, cache)


def get_cache_key_answer(question: str, user_answer: str) -> str:
    """Generate a cache key for answer evaluation."""
    combined = f"{question}_{user_answer}".lower()
    return hashlib.md5(combined.encode()).hexdigest()[:12]


def get_cached_evaluation(question: str, user_answer: str) -> Optional[Dict]:
    """Retrieve a cached evaluation if available."""
    cache = load_json_cache(ANSWERS_CACHE)
    key = get_cache_key_answer(question, user_answer)
    if key in cache:
        return cache[key]
    return None


def cache_evaluation(question: str, user_answer: str, evaluation_data: Dict):
    """Store an evaluation result in cache."""
    ensure_cache_dir()
    cache = load_json_cache(ANSWERS_CACHE)
    key = get_cache_key_answer(question, user_answer)
    cache[key] = evaluation_data
    save_json_cache(ANSWERS_CACHE, cache)


class RateLimiter:
    """Handle rate limiting with exponential backoff for quota-exceeded errors."""
    
    def __init__(self, initial_delay: float = 1.0, max_retries: int = 3):
        self.initial_delay = initial_delay
        self.max_retries = max_retries
    
    def call_with_backoff(self, func, *args, **kwargs) -> Any:
        """Execute function with exponential backoff on rate limit errors."""
        delay = self.initial_delay
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except api_exceptions.ResourceExhausted as e:
                if attempt < self.max_retries - 1:
                    print(f"⏳ Rate limit hit. Retrying in {delay:.1f}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"❌ Quota exhausted after {self.max_retries} attempts. Please wait before retrying.")
                    raise
            except Exception as e:
                # Don't retry on other exceptions
                raise
