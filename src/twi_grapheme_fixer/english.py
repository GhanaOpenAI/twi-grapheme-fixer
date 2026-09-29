"""
English word detection and exemption logic for Twi text processing.

Prevents English loanwords, code-switched phrases, and foreign tokens from
being corrupted by Twi Advanced Tongue Root (ATR) vowel harmony transformations.
"""

from __future__ import annotations

import gzip
from functools import lru_cache
from importlib import resources
from typing import Optional, Set

from .rules import LAX_VOWELS, NON_TWI_LETTERS, PROTECTED_TWI_WORDS

# English morphological suffixes that strongly indicate English words
ENGLISH_SUFFIXES = (
    "ing", "tion", "sion", "ment", "able", "ible", "ness",
    "ity", "ive", "ous", "ful", "less", "ism", "ist",
)


@lru_cache(maxsize=1)
def get_english_lexicon() -> Set[str]:
    """Load the embedded gzipped English lexicon (over 400,000 words)."""
    try:
        ref = resources.files("twi_grapheme_fixer.data").joinpath("words_en.txt.gz")
        with ref.open("rb") as f_raw:
            with gzip.open(f_raw, "rt", encoding="utf-8") as f:
                return set(f.read().splitlines())
    except Exception:
        # Fallback for direct local path if importlib package is not installed in editable mode yet
        from pathlib import Path
        local_path = Path(__file__).parent / "data" / "words_en.txt.gz"
        with gzip.open(local_path, "rt", encoding="utf-8") as f:
            return set(f.read().splitlines())


@lru_cache(maxsize=1)
def get_twi_lexicon() -> Set[str]:
    """Load the embedded gzipped Twi lexicon."""
    try:
        ref = resources.files("twi_grapheme_fixer.data").joinpath("words_twi.txt.gz")
        with ref.open("rb") as f_raw:
            with gzip.open(f_raw, "rt", encoding="utf-8") as f:
                return set(f.read().splitlines())
    except Exception:
        from pathlib import Path
        local_path = Path(__file__).parent / "data" / "words_twi.txt.gz"
        with gzip.open(local_path, "rt", encoding="utf-8") as f:
            return set(f.read().splitlines())


def is_english_word(
    word: str,
    custom_exempt: Optional[Set[str]] = None,
    custom_twi: Optional[Set[str]] = None,
    english_vocab: Optional[Set[str]] = None,
    twi_vocab: Optional[Set[str]] = None,
) -> bool:
    """
    Determine whether a word should be treated as English/foreign.

    Evaluation steps:
    1. User custom overrides (custom_twi / custom_exempt)
    2. Akan-specific characters (ɛ, ɔ, ë, ö, à, ô, é) -> definitively Twi
    3. Non-Twi letters (c, j, q, v, x, z) -> definitively foreign/English
    4. Protected Twi homographs (words like 'no', 'me', 'se') -> Twi
    5. English vocabulary lookup -> English
    6. English morphological and phonotactic rules -> English
    7. Twi vocabulary lookup -> Twi
    """
    if not word:
        return False

    w = word.lower()

    # Step 1: User custom overrides
    if custom_twi and w in custom_twi:
        return False
    if custom_exempt and w in custom_exempt:
        return True

    # Step 2: Unambiguous Twi / Akan characters
    if any(c in "ɛɔƐƆëöËÖàÀôÔéÉ" for c in word):
        return False

    # Step 3: Native Akan does not have letters c, j, q, v, x, z
    if any(c in NON_TWI_LETTERS for c in word):
        return True

    # Step 4: Protected Twi words (homographs like 'no', 'so', 'me', 'ne', 'se')
    if w in PROTECTED_TWI_WORDS:
        return False

    # Step 5: Lexicon lookups
    en_words = english_vocab if english_vocab is not None else get_english_lexicon()
    if w in en_words:
        return True

    # Step 6: Morphological suffix heuristics for compound/inflected English
    if any(w.endswith(sfx) for sfx in ENGLISH_SUFFIXES):
        return True

    # Step 7: Check Twi vocabulary
    tw_words = twi_vocab if twi_vocab is not None else get_twi_lexicon()
    if w in tw_words:
        return False

    # Default: if not verified as English, allow Twi harmony rules
    return False
