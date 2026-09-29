import pytest
from twi_grapheme_fixer import TwiGraphemeFixer, fix_graphemes, is_english_word


def test_detect_non_twi_alphabet_letters():
    # Words with c, j, q, v, x, z must be detected as English / foreign
    assert is_english_word("school")
    assert is_english_word("church")
    assert is_english_word("service")
    assert is_english_word("project")
    assert is_english_word("victory")
    assert is_english_word("zero")
    assert is_english_word("quick")
    assert is_english_word("exercise")
    assert is_english_word("judge")


def test_detect_common_english_words_without_foreign_letters():
    # Words like hospital, phone, welcome, people, morning, etc. only use letters in Akan,
    # but are English words and must be recognized and exempt
    assert is_english_word("hospital")
    assert is_english_word("phone")
    assert is_english_word("telephone")
    assert is_english_word("welcome")
    assert is_english_word("people")
    assert is_english_word("morning")
    assert is_english_word("yesterday")
    assert is_english_word("government")
    assert is_english_word("table")
    assert is_english_word("problem")


def test_twi_words_not_detected_as_english():
    # Essential Twi words must not be detected as English
    assert not is_english_word("aduane")
    assert not is_english_word("pono")
    assert not is_english_word("ɛsono")
    assert not is_english_word("awurade")
    assert not is_english_word("twene")
    assert not is_english_word("kronkron")
    assert not is_english_word("fononoo")
    # Homographs
    assert not is_english_word("no")
    assert not is_english_word("so")
    assert not is_english_word("me")
    assert not is_english_word("ne")
    assert not is_english_word("se")


def test_mixed_sentence_conversion():
    fixer = TwiGraphemeFixer(exempt_english=True)
    sentence = "Good morning, me nua, kɔ school na wobɛnya aduane no."
    res = fixer.convert(sentence)
    # English words 'Good', 'morning', 'school' should be untouched
    assert "Good" in res
    assert "morning" in res
    assert "school" in res
    # Twi words should be converted
    assert "mé" in res
    assert "àduané" in res
    assert "nô" in res


def test_mixed_code_switching_loanwords():
    fixer = TwiGraphemeFixer(exempt_english=True)
    sentence = "Ɔkae dɛ me phone no gu table no so."
    res = fixer.convert(sentence)
    # phone and table remain English
    assert "phone" in res
    assert "table" in res
    # Twi particles converted
    assert "mé" in res
    assert "nô" in res
    assert "sô" in res


def test_disable_english_exemption():
    # When disabled, all words including English are treated as Twi
    fixer = TwiGraphemeFixer(exempt_english=False)
    sentence = "school phone"
    res = fixer.convert(sentence)
    # 'school' has oo -> ôô, 'phone' has o -> ô, e -> é
    assert res == "schôôl phôné"


def test_custom_overrides():
    # Custom exempt word
    fixer = TwiGraphemeFixer(custom_exempt_words={"mybrand"})
    assert fixer.is_english("mybrand")

    # Custom twi word override
    fixer_twi = TwiGraphemeFixer(custom_twi_words={"phone"})
    assert not fixer_twi.is_english("phone")
    assert fixer_twi.convert("phone") == "phôné"
