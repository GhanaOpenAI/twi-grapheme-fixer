"""
Core Twi grapheme converter engine.

Applies Twi Advanced Tongue Root (ATR) vowel harmony transformations,
optional extended character normalization (ɔ->ö, ɛ->ë), and English
word exemption for speech datasets (ASR/TTS) and text normalization.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from .english import get_english_lexicon, get_twi_lexicon, is_english_word
from .rules import (
    A_FORWARD,
    A_REVERSE,
    DEFAULT_EXCEPTIONS_FORWARD,
    DEFAULT_EXCEPTIONS_REVERSE,
    E_FORWARD,
    E_REVERSE,
    EXTENDED_FORWARD,
    EXTENDED_REVERSE,
    LAX_VOWELS,
    O_FORWARD,
    O_REVERSE,
    PROTECTED_TWI_WORDS,
    TRIGGER_VOWELS,
)

# Regex pattern splitting text on word boundaries while retaining punctuation and whitespace
_TOKEN_PATTERN = re.compile(r"(\b[^\W\d_]+\b)", re.UNICODE)


def match_case(src: str, dst: str) -> str:
    """Carry source token's capitalisation over to the destination token."""
    if src.isupper():
        return dst.upper()
    if src and src[0].isupper():
        return dst[0].upper() + dst[1:]
    return dst


def replace_extended_chars(text: str) -> str:
    """
    Replace extended Akan characters with Unicode diaeresis equivalents.

    ɔ -> ö, Ɔ -> Ö, ɛ -> ë, Ɛ -> Ë
    """
    return "".join(EXTENDED_FORWARD.get(c, c) for c in text)


def restore_extended_chars(text: str) -> str:
    """
    Restore Unicode diaeresis equivalents back to standard extended Akan characters.

    ö -> ɔ, Ö -> Ɔ, ë -> ɛ, Ë -> Ɛ
    """
    return "".join(EXTENDED_REVERSE.get(c, c) for c in text)


class TwiGraphemeFixer:
    """
    Twi grapheme and vowel harmony converter with English exemption.

    Parameters
    ----------
    exempt_english : bool, default True
        Whether to exempt English loanwords and code-switched words from Twi rules.
    replace_extended : bool, default False
        Whether to replace extended chars (ɔ->ö, ɛ->ë) in forward conversion.
    custom_exceptions : dict, optional
        Custom word-level overrides mapping input word to target word.
    custom_exempt_words : set, optional
        Additional words to treat as English/exempt from conversion.
    custom_twi_words : set, optional
        Additional words to force-treat as Twi (never exempt).
    """

    def __init__(
        self,
        exempt_english: bool = True,
        replace_extended: bool = False,
        custom_exceptions: Optional[Dict[str, str]] = None,
        custom_exempt_words: Optional[Union[Set[str], Iterable[str]]] = None,
        custom_twi_words: Optional[Union[Set[str], Iterable[str]]] = None,
    ):
        self.exempt_english = exempt_english
        self.replace_extended = replace_extended

        # Build exceptions dictionaries
        self.exceptions_forward = dict(DEFAULT_EXCEPTIONS_FORWARD)
        if custom_exceptions:
            self.exceptions_forward.update(custom_exceptions)
        self.exceptions_reverse = {v: k for k, v in self.exceptions_forward.items()}

        self.custom_exempt_words = set(custom_exempt_words) if custom_exempt_words else None
        self.custom_twi_words = set(custom_twi_words) if custom_twi_words else None

        # Pre-load lexicons if English exemption is active
        if self.exempt_english:
            self.en_vocab = get_english_lexicon()
            self.twi_vocab = get_twi_lexicon()
        else:
            self.en_vocab = None
            self.twi_vocab = None

    def is_english(self, word: str) -> bool:
        """Check if a word is identified as English/exempt."""
        if not self.exempt_english:
            return False
        return is_english_word(
            word,
            custom_exempt=self.custom_exempt_words,
            custom_twi=self.custom_twi_words,
            english_vocab=self.en_vocab,
            twi_vocab=self.twi_vocab,
        )

    def process_word(
        self,
        word: str,
        direction: str = "forward",
        replace_extended: Optional[bool] = None,
    ) -> Tuple[str, bool]:
        """
        Process a single word.

        Returns (converted_word, is_exempt).
        """
        if not word:
            return word, False

        do_replace_ext = self.replace_extended if replace_extended is None else replace_extended

        if direction == "forward":
            # Check English exemption
            if self.exempt_english and self.is_english(word):
                return word, True

            # Check lexical exceptions
            if word in self.exceptions_forward:
                res = self.exceptions_forward[word]
                if do_replace_ext:
                    res = replace_extended_chars(res)
                return res, False

            lw = word.lower()
            if lw in self.exceptions_forward:
                rep = self.exceptions_forward[lw]
                res = match_case(word, rep)
                if do_replace_ext:
                    res = replace_extended_chars(res)
                return res, False

            chars = list(word)
            n = len(chars)

            for i in range(n):
                ch = chars[i]
                lower = ch.lower()

                if lower == "a":
                    # Regressive harmony: i/u trigger later in the word,
                    # blocked only by an unambiguous -ATR vowel (ɛ/ɔ or ë/ö)
                    rest = "".join(chars[i + 1:])
                    has_trigger = bool(re.search(f"[{TRIGGER_VOWELS}]", rest))
                    has_blocker = bool(re.search(f"[{LAX_VOWELS}]", rest))
                    if has_trigger and not has_blocker:
                        chars[i] = "À" if ch.isupper() else "à"
                elif lower == "o":
                    chars[i] = "Ô" if ch.isupper() else "ô"
                elif lower == "e":
                    chars[i] = "É" if ch.isupper() else "é"

            res = "".join(chars)
            if do_replace_ext:
                res = replace_extended_chars(res)
            return res, False

        else:
            # Reverse direction
            # If word is in reverse exceptions
            if word in self.exceptions_reverse:
                return self.exceptions_reverse[word], False

            lw = word.lower()
            if lw in self.exceptions_reverse:
                rep = self.exceptions_reverse[lw]
                return match_case(word, rep), False

            chars = list(word)
            for i, ch in enumerate(chars):
                if ch in A_REVERSE:
                    chars[i] = A_REVERSE[ch]
                elif ch in O_REVERSE:
                    chars[i] = O_REVERSE[ch]
                elif ch in E_REVERSE:
                    chars[i] = E_REVERSE[ch]

            res = "".join(chars)
            if do_replace_ext:
                res = restore_extended_chars(res)
            return res, False

    def convert(
        self,
        text: str,
        direction: str = "forward",
        replace_extended: Optional[bool] = None,
    ) -> str:
        """
        Convert text using Twi grapheme rules.

        Parameters
        ----------
        text : str
            Input text to process.
        direction : str, default 'forward'
            'forward' to apply rules, 'reverse' to revert them.
        replace_extended : bool, optional
            Override instance setting for replacing extended chars (ɔ->ö, ɛ->ë).

        Returns
        -------
        str : The converted text.
        """
        if not text:
            return text

        tokens = _TOKEN_PATTERN.split(text)
        out = []
        for t in tokens:
            if t and (t.isalpha() or not re.search(r"[\W\d_]", t)):
                converted, _ = self.process_word(t, direction=direction, replace_extended=replace_extended)
                out.append(converted)
            else:
                out.append(t)
        return "".join(out)

    def convert_with_report(
        self,
        text: str,
        direction: str = "forward",
        replace_extended: Optional[bool] = None,
    ) -> Tuple[str, Dict]:
        """Convert text and return conversion metrics and exempt tokens."""
        if not text:
            return text, {"total_words": 0, "converted": 0, "exempt_english": 0, "exempt_tokens": []}

        tokens = _TOKEN_PATTERN.split(text)
        out = []
        total_words = 0
        converted_count = 0
        exempt_count = 0
        exempt_tokens = []

        for t in tokens:
            if t and (t.isalpha() or not re.search(r"[\W\d_]", t)):
                total_words += 1
                converted, is_exempt = self.process_word(
                    t, direction=direction, replace_extended=replace_extended
                )
                if is_exempt:
                    exempt_count += 1
                    exempt_tokens.append(t)
                elif converted != t:
                    converted_count += 1
                out.append(converted)
            else:
                out.append(t)

        report = {
            "total_words": total_words,
            "converted": converted_count,
            "exempt_english": exempt_count,
            "exempt_tokens": exempt_tokens,
        }
        return "".join(out), report

    def convert_batch(
        self,
        texts: Iterable[str],
        direction: str = "forward",
        replace_extended: Optional[bool] = None,
    ) -> List[str]:
        """Convert an iterable of text strings."""
        return [self.convert(t, direction=direction, replace_extended=replace_extended) for t in texts]

    def convert_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        direction: str = "forward",
        replace_extended: Optional[bool] = None,
    ) -> int:
        """
        Convert a text file line-by-line.

        Returns total number of lines processed.
        """
        inp = Path(input_path)
        outp = Path(output_path)
        count = 0
        with open(inp, "r", encoding="utf-8") as f_in, open(outp, "w", encoding="utf-8") as f_out:
            for line in f_in:
                f_out.write(self.convert(line, direction=direction, replace_extended=replace_extended))
                count += 1
        return count


# Functional convenience wrappers

def fix_graphemes(
    text: str,
    direction: str = "forward",
    exempt_english: bool = True,
    replace_extended: bool = False,
    custom_exceptions: Optional[Dict[str, str]] = None,
    custom_exempt_words: Optional[Union[Set[str], Iterable[str]]] = None,
    custom_twi_words: Optional[Union[Set[str], Iterable[str]]] = None,
) -> str:
    """
    Apply Twi ATR vowel harmony and grapheme fixes to text.

    Parameters
    ----------
    text : str
        Input text to process.
    direction : str, default 'forward'
        'forward' to apply rules, 'reverse' to restore original orthography.
    exempt_english : bool, default True
        Exempt English words from harmony shifts.
    replace_extended : bool, default False
        Convert extended vowels (ɔ->ö, ɛ->ë).
    """
    fixer = TwiGraphemeFixer(
        exempt_english=exempt_english,
        replace_extended=replace_extended,
        custom_exceptions=custom_exceptions,
        custom_exempt_words=custom_exempt_words,
        custom_twi_words=custom_twi_words,
    )
    return fixer.convert(text, direction=direction)


def unfix_graphemes(
    text: str,
    restore_extended: bool = False,
    custom_exceptions: Optional[Dict[str, str]] = None,
) -> str:
    """
    Restore fixed Twi graphemes back to standard orthography.

    Parameters
    ----------
    text : str
        Text containing fixed graphemes (à, ô, é).
    restore_extended : bool, default False
        Also restore ö->ɔ and ë->ɛ.
    """
    fixer = TwiGraphemeFixer(
        exempt_english=False,
        replace_extended=restore_extended,
        custom_exceptions=custom_exceptions,
    )
    return fixer.convert(text, direction="reverse", replace_extended=restore_extended)
