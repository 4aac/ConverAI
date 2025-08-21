# services/topics.py
import os
import random
from typing import List

# Default fallback topics if file is missing/empty
_DEFAULT_TOPICS = [
    "Casual conversation",
    "Travel & Airports",
    "University life",
    "Housing & Accommodation",
    "Restaurant ordering",
]

_TOPICS_CACHE: List[str] = []

# Resolve data/topics.txt relative to this file, unless TOPICS_PATH is provided
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../backend
_FALLBACK_PATH = os.path.join(_BASE_DIR, "data", "topics.txt")
_TOPICS_PATH = os.getenv("TOPICS_PATH", _FALLBACK_PATH)


def _load_topics() -> List[str]:
    if not os.path.exists(_TOPICS_PATH):
        return _DEFAULT_TOPICS[:]
    topics: List[str] = []
    with open(_TOPICS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t and not t.startswith("#"):
                topics.append(t)
    return topics or _DEFAULT_TOPICS[:]


def get_random_topic() -> str:
    global _TOPICS_CACHE
    if not _TOPICS_CACHE:
        _TOPICS_CACHE = _load_topics()
    return random.choice(_TOPICS_CACHE)
