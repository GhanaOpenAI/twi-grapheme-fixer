import pytest
from twi_grapheme_fixer import (
    TwiGraphemeFixer,
    fix_graphemes,
    replace_extended_chars,
    restore_extended_chars,
    unfix_graphemes,
)


def test_replace_extended_chars_direct():
    text = "ɔte fie na ɔkɔɔ asɔre, me nua ɛna"
    replaced = replace_extended_chars(text)
    assert "ö" in replaced
    assert "ë" in replaced
    assert "ɔ" not in replaced
    assert "ɛ" not in replaced

    restored = restore_extended_chars(replaced)
    assert restored == text


def test_extended_capitalization():
    assert replace_extended_chars("Ɔman") == "Öman"
    assert replace_extended_chars("Ɛna") == "Ëna"
    assert restore_extended_chars("Öman") == "Ɔman"
    assert restore_extended_chars("Ëna") == "Ɛna"


def test_combined_harmony_and_extended():
    fixer = TwiGraphemeFixer(replace_extended=True)
    fwd = fixer.convert("bɛsane")
    assert fwd == "bësané"

    fwd_esono = fixer.convert("ɛsono")
    assert fwd_esono == "ësôno"

    # Reverse
    rev = fixer.convert(fwd, direction="reverse")
    assert rev == "bɛsane"
    rev_esono = fixer.convert(fwd_esono, direction="reverse")
    assert rev_esono == "ɛsono"


def test_round_trip_all_samples_with_extended():
    samples = [
        "aduane", "bɛsane", "ahosɛpɛ", "awerɛhoɔ",
        "pono", "no", "fononoo", "ɛsono", "kronkron",
        "se", "pene", "abene", "twene", "agye", "bɛtenaa",
        "atentene", "ɔmane", "afɔdeɛ", "awurade",
    ]
    fixer = TwiGraphemeFixer(replace_extended=True)
    for word in samples:
        fwd = fixer.convert(word, direction="forward")
        rev = fixer.convert(fwd, direction="reverse")
        assert rev == word, f"Extended round-trip failed: {word} -> {fwd} -> {rev}"
