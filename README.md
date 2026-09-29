# Twi Grapheme Fixer (Twi G2G)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GhanaOpenAI](https://img.shields.io/badge/Org-GhanaOpenAI-black.svg)](https://github.com/GhanaOpenAI)

A fast, lightweight, and linguistically grounded grapheme-to-grapheme normalizer for **Twi (Akan)**. It resolves **Advanced Tongue Root (ATR)** vowel harmony ambiguities and replaces extended characters for speech model training (ASR/TTS), while **intelligently exempting English loanwords and code-switched text**.

---

## 🎯 The Motivation

Standard written Akan/Twi orthography uses a 7-letter vowel alphabet (`a, e, ɛ, i, o, ɔ, u`) to represent what is phonologically a **9-to-10 vowel system** governed by **Advanced Tongue Root (ATR)** vowel harmony:

- **[+ATR] vowels**: `/i/, /e̘/, /o̘/, /u/` and the raised low allophone `[æ]` (or `[a̘]`)
- **[-ATR] vowels**: `/ɪ/, /ɛ/, /ɔ/, /ʊ/, /a/`

Because the orthography does not mark these acoustic distinctions:
1. **Low Vowel Ambiguity (`a`)**: The letter `a` represents both the retracted `[a]` (in *papa*) and the advanced `[æ]` (in *aduane*, *awurade*) triggered by regressive harmony from trailing high vowels (`i, u`).
2. **Mid Vowel Ambiguity (`e`, `o`)**: Plain `e` and `o` are [+ATR] vowels, but standard text conflates dialectal and lexical nuances with lax equivalents.
3. **ASR & TTS Impact**: When training acoustic models (Wav2Vec2, Whisper, Conformer, Piper, VITS), identical graphemes map to distinct acoustic distributions, increasing Word Error Rate (WER) and confusing phoneme aligners.

### The Code-Switching Challenge
In real-world Ghanaian text and ASR corpora, **code-switching with English is ubiquitous** (e.g., *"Kofi kɔɔ school yesterday"*, *"Me phone no yerae"*). Naive rule-based converters mutate English words into broken pseudo-Twi:
- `school` ➔ `schôôl`
- `hospital` ➔ `hôspìtal`
- `phone` ➔ `phônê`
- `welcome` ➔ `wélcômé`
- `morning` ➔ `môrnìng`

**`twi-grapheme-fixer` solves this problem** by pairing deterministic phonological rules with a 400,000+ word English exemption engine and protected Akan homograph handling.

---

## ✨ Key Features

- **Linguistically Accurate ATR Harmony**:
  - `a ➔ à`: Triggered regressively by trailing `i` or `u`, and blocked by unambiguous [-ATR] vowels (`ɛ`, `ɔ`).
  - `o ➔ ô`: Marks standard [+ATR] mid-back vowel.
  - `e ➔ é`: Marks standard [+ATR] mid-front vowel.
- **Lexical Exceptions**: Handles known lexical exceptions (e.g. `ɛsono ➔ ɛsôno`, `twene ➔ twéne`, `atentene ➔ aténtené`).
- **Smart English Exemption**:
  - Over 400,000 embedded English words and inflections.
  - Detects non-Twi alphabet letters (`c, j, q, v, x, z`).
  - Identifies foreign consonant codas and morphology (`-ing`, `-tion`, etc.).
  - **Homograph Protection**: Guarantees core Twi grammatical particles (`no`, `me`, `ne`, `so`, `se`, `mu`, `wo`, etc.) are always correctly converted.
- **Extended Character Normalization (`ɔ ➔ ö`, `ɛ ➔ ë`)**:
  - Optional flag for standard Latin-1 / BPE tokenizer compatibility in models that lack African reference alphabet symbols.
- **100% Lossless Round-Trip**:
  - Full bidirectional support (`forward` and `reverse`).
- **Zero Runtime Dependencies**: Pure Python standard library implementation, blazing fast (< 30ms startup).

---

## 📦 Installation

```bash
git clone https://github.com/GhanaOpenAI/twi-grapheme-fixer.git
cd twi-grapheme-fixer
pip install .
```

---

## 🚀 Quickstart

### 1. Python API

```python
from twi_grapheme_fixer import fix_graphemes, unfix_graphemes

# Basic Twi conversion
text = "aduane ne pono wɔ fie no"
fixed = fix_graphemes(text)
print(fixed)
# Output: àduané né pônô wɔ fié nô

# Round-trip restoration
restored = unfix_graphemes(fixed)
print(restored)
# Output: aduane ne pono wɔ fie no

# Mixed Twi and English code-switching
mixed = "Good morning, me nua, kɔ school na wobɛnya aduane no."
fixed_mixed = fix_graphemes(mixed)
print(fixed_mixed)
# Output: Good morning, mé nua, kɔ school na wôbɛnya àduané nô.
# Note: 'Good', 'morning', and 'school' are untouched!
```

### 2. Extended Character Replacement (`ɔ ➔ ö`, `ɛ ➔ ë`)

For tokenizers or acoustic models that don't support extended characters:

```python
from twi_grapheme_fixer import fix_graphemes

fixed = fix_graphemes("bɛsane ɛsono", replace_extended=True)
print(fixed)
# Output: bësané ësôno

# Restoring back to standard Twi orthography
restored = fix_graphemes(fixed, direction="reverse", replace_extended=True)
print(restored)
# Output: bɛsane ɛsono
```

### 3. Object-Oriented Batch Processing

```python
from twi_grapheme_fixer import TwiGraphemeFixer

fixer = TwiGraphemeFixer(
    exempt_english=True,
    replace_extended=False
)

# Convert list of lines
lines = [
    "Kofi kɔɔ school no mu",
    "Ɔkae dɛ me phone no gu table no so"
]
processed = fixer.convert_batch(lines)
for line in processed:
    print(line)

# Convert an entire dataset file
fixer.convert_file("transcripts.txt", "transcripts_fixed.txt")
```

---

## 💻 CLI Usage

The package installs both `twi-fixer` and `twi-grapheme-fixer` command-line executables:

```bash
# Direct string input
twi-fixer "Good morning, me nua, kɔ school na wobɛnya aduane no"

# Pipe through stdin / stdout
cat input.txt | twi-fixer > output.txt

# File conversion
twi-fixer -i transcripts.txt -o transcripts_fixed.txt

# Reverse back to standard Twi
twi-fixer -d reverse -i transcripts_fixed.txt -o restored.txt

# Replace extended characters (ɔ -> ö, ɛ -> ë)
twi-fixer --replace-extended "ɛsono kɛseɛ"

# Detailed report showing exempted English words
twi-fixer --report "Kofi went to the hospital yesterday"
```

Output with `--report`:
```
--- Twi Grapheme Fixer Report ---
Total words:      6
Words converted:  1
English exempted: 5
Exempt samples:   went, to, the, hospital, yesterday
```

---

## 📊 Summary of Transformation Rules

| Input | Output | Linguistic Rule | Example | Result |
| :--- | :--- | :--- | :--- | :--- |
| `a` | `à` | Regressive harmony triggered by trailing `i`/`u` | `aduane` | `àduané` |
| `a` | `a` | Blocked by lax vowel (`ɛ`, `ɔ`) or no trigger | `bɛsane` | `bɛsané` |
| `o` | `ô` | Default [+ATR] mid-back vowel | `pono`, `no` | `pônô`, `nô` |
| `e` | `é` | Default [+ATR] mid-front vowel | `se`, `pene` | `sé`, `péné` |
| `ɛsono` | `ɛsôno` | Lexical exception (second vowel is lax) | `ɛsono` | `ɛsôno` |
| `twene` | `twéne` | Lexical exception | `twene` | `twéne` |
| `atentene` | `aténtené`| Lexical exception | `atentene` | `aténtené` |
| `ɔ` | `ö` | *(Optional)* Extended char replacement | `ɔmane` | `ömané` |
| `ɛ` | `ë` | *(Optional)* Extended char replacement | `afɔdeɛ` | `afödéë` |
| `school` | `school` | **English exemption**: preserved as English | `kɔ school` | `kɔ school` |

---

## 🔬 Integration with ASR Pipelines (Hugging Face Datasets)

```python
from datasets import load_dataset
from twi_grapheme_fixer import fix_graphemes

dataset = load_dataset("GhanaNLP/twi_speech_corpus", split="train")

def preprocess_transcripts(batch):
    batch["sentence"] = [fix_graphemes(text) for text in batch["sentence"]]
    return batch

dataset = dataset.map(preprocess_transcripts, batched=True)
```

---

## 🧪 Running Tests

```bash
git clone https://github.com/GhanaOpenAI/twi-grapheme-fixer.git
cd twi-grapheme-fixer
python3 -m pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **GhanaOpenAI** and contributors to advance NLP and speech technologies for Ghanaian languages.
