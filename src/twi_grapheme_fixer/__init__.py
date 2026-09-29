"""
twi-grapheme-fixer
~~~~~~~~~~~~~~~~~~
A toolkit for fixing Twi (Akan) graphemes using Advanced Tongue Root (ATR)
vowel harmony rules and extended character representations, with built-in
English loanword/code-switching exemption for robust ASR & TTS dataset preparation.
"""

from .converter import (
    TwiGraphemeFixer,
    fix_graphemes,
    replace_extended_chars,
    restore_extended_chars,
    unfix_graphemes,
)
from .english import get_english_lexicon, get_twi_lexicon, is_english_word

__version__ = "0.1.0"

__all__ = [
    "TwiGraphemeFixer",
    "fix_graphemes",
    "unfix_graphemes",
    "replace_extended_chars",
    "restore_extended_chars",
    "is_english_word",
    "get_english_lexicon",
    "get_twi_lexicon",
    "__version__",
]
