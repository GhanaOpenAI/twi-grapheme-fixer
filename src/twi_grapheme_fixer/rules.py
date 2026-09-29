"""
Twi grapheme and vowel harmony rule definitions.

Defines the character mappings for Advanced Tongue Root (ATR) vowel harmony,
extended character substitutions, and phonological trigger/blocker sets.
"""

from __future__ import annotations

# ATR vowel harmony forward and reverse mappings
A_FORWARD = {"a": "à", "A": "À"}
A_REVERSE = {v: k for k, v in A_FORWARD.items()}

O_FORWARD = {"o": "ô", "O": "Ô"}
O_REVERSE = {v: k for k, v in O_FORWARD.items()}

E_FORWARD = {"e": "é", "E": "É"}
E_REVERSE = {v: k for k, v in E_FORWARD.items()}

# Extended characters to standard Unicode diaeresis / umlauts
# Useful for tokenizers or acoustic models that lack open-e (ɛ) and open-o (ɔ)
EXTENDED_FORWARD = {
    "ɔ": "ö",
    "Ɔ": "Ö",
    "ɛ": "ë",
    "Ɛ": "Ë",
}
EXTENDED_REVERSE = {v: k for k, v in EXTENDED_FORWARD.items()}

# +ATR high vowels that trigger regressive harmony on 'a'
TRIGGER_VOWELS = "iuIU"

# Lax (-ATR) vowels that block harmony on 'a' (including diaeresis forms)
LAX_VOWELS = "ɛɔƐƆëöËÖ"

# Characters that do not belong to the native 22-letter Akan/Twi alphabet
NON_TWI_LETTERS = set("cjqvxzCJQVXZ")

# Lexical exceptions: words where 'o' or 'e' do not follow the uniform +ATR rule
DEFAULT_EXCEPTIONS_FORWARD: dict[str, str] = {
    "ɛsono": "ɛsôno",
    "twene": "twéne",
    "atentene": "aténtené",
}
DEFAULT_EXCEPTIONS_REVERSE: dict[str, str] = {
    v: k for k, v in DEFAULT_EXCEPTIONS_FORWARD.items()
}

# High-frequency Twi words and homographs with English words that must always
# be treated as Twi (preventing English exemption from masking them)
PROTECTED_TWI_WORDS: set[str] = {
    "no", "so", "me", "ne", "se", "wo", "ye", "mu", "yi", "ho",
    "na", "ma", "ba", "fa", "ka", "di", "sa", "bo", "bu", "da",
    "wɔ", "kɔ", "baa", "ha", "pa", "pe", "bi", "de", "din",
    "dan", "dua", "nan", "nsa", "ti", "fie", "efie", "ofie",
    "kwan", "kasa", "asem", "asɛm", "anim", "obi", "ebia", "nanso", "enti",
    "hwee", "nhoma", "asore", "onipa", "nyame", "abofra", "mmofra",
    "pono", "aduane", "fononoo", "kronkron", "pene", "abene", "twene",
    "agye", "awurade", "atentene", "sane", "sere", "mono", "dodo",
    "kane", "kama", "dada", "mane", "papa", "tutu", "ama", "kofi",
    "kwame", "kwasi", "kwadwo", "kwabena", "yaw", "afia", "akua",
    "bɛsane", "ahosɛpɛ", "awerɛhoɔ", "ɛsono", "bɛtenaa", "ɔmane", "afɔdeɛ",
    "anɔpa", "awia", "anwummere", "anadwo", "nnɛ", "ɔkyena", "nkyɛ", "dabi",
    "nkrataa", "nhwehwɛmu", "gyae", "gyina", "tena", "dwom",
}
