import pytest
from twi_grapheme_fixer import TwiGraphemeFixer, fix_graphemes, unfix_graphemes

SAMPLE_WORDS = [
    "aduane", "bɛsane", "ahosɛpɛ", "awerɛhoɔ",
    "pono", "no", "fononoo", "ɛsono", "kronkron",
    "se", "pene", "abene", "twene", "agye", "bɛtenaa",
    "atentene", "ɔmane", "afɔdeɛ", "awurade",
]

EXPECTED_FORWARD = {
    "aduane": "àduané",
    "bɛsane": "bɛsané",
    "ahosɛpɛ": "ahôsɛpɛ",
    "awerɛhoɔ": "awérɛhôɔ",
    "pono": "pônô",
    "no": "nô",
    "fononoo": "fônônôô",
    "ɛsono": "ɛsôno",
    "kronkron": "krônkrôn",
    "se": "sé",
    "pene": "péné",
    "abene": "abéné",
    "twene": "twéne",
    "agye": "agyé",
    "bɛtenaa": "bɛténaa",
    "atentene": "aténtené",
    "ɔmane": "ɔmané",
    "afɔdeɛ": "afɔdéɛ",
    "awurade": "àwuradé",
}


def test_sample_words_forward():
    for word in SAMPLE_WORDS:
        fwd = fix_graphemes(word, direction="forward")
        assert fwd == EXPECTED_FORWARD[word], f"Failed forward conversion for '{word}': got '{fwd}', expected '{EXPECTED_FORWARD[word]}'"


def test_round_trip_sample_words():
    for word in SAMPLE_WORDS:
        fwd = fix_graphemes(word, direction="forward")
        rev = fix_graphemes(fwd, direction="reverse")
        assert rev == word, f"Round-trip failed for '{word}': {word} -> {fwd} -> {rev}"


def test_case_preservation():
    assert fix_graphemes("Aduane") == "Àduané"
    assert fix_graphemes("ADUANE") == "ÀDUANÉ"
    assert fix_graphemes("Ɛsono") == "Ɛsôno"
    assert fix_graphemes("ƐSONO") == "ƐSÔNO"
    assert fix_graphemes("Twene") == "Twéne"
    assert fix_graphemes("TWENE") == "TWÉNE"


def test_regressive_harmony_on_a():
    # 'a' followed by 'u' without blocker -> à
    assert fix_graphemes("awurade") == "àwuradé"
    # 'a' followed by 'i' without blocker -> à
    assert fix_graphemes("ani") == "ànì" or fix_graphemes("akyi") == "àkyi"


def test_lax_vowel_blocking():
    # 'a' followed by 'u' or 'i', but blocked by 'ɛ' or 'ɔ'
    # in bɛsane, preceding ɛ is lax and there's no trailing trigger
    assert fix_graphemes("bɛsane") == "bɛsané"


def test_batch_and_file_conversion(tmp_path):
    fixer = TwiGraphemeFixer(exempt_english=True)
    texts = ["aduane ne pono", "awurade kɛseɛ", "ɛsono kɛse"]
    results = fixer.convert_batch(texts)
    assert len(results) == 3
    assert results[0] == "àduané né pônô"

    in_file = tmp_path / "input.txt"
    out_file = tmp_path / "output.txt"
    in_file.write_text("\n".join(texts), encoding="utf-8")

    count = fixer.convert_file(in_file, out_file)
    assert count == 3
    converted_lines = out_file.read_text(encoding="utf-8").splitlines()
    assert converted_lines == results


def test_empty_and_whitespace():
    assert fix_graphemes("") == ""
    assert fix_graphemes("   \n\t  ") == "   \n\t  "
    assert unfix_graphemes("") == ""


def test_punctuation_and_numbers():
    text = "Kofi wɔ 500 cedis, 'aduane' ne \"pono\"! (ɛsono)?"
    fixed = fix_graphemes(text)
    assert "500" in fixed
    assert "cedis" in fixed  # English loanword
    assert "àduané" in fixed
    assert "pônô" in fixed
    assert "ɛsôno" in fixed
    assert fixed.startswith("Kôfi wɔ 500")

    restored = unfix_graphemes(fixed)
    assert restored == "Kofi wɔ 500 cedis, 'aduane' ne \"pono\"! (ɛsono)?"

