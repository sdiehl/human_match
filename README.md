# Human Name Matching Engine

Matching human names is a [complex problem](https://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/) that spans across languages, writing systems, and cultural conventions. This library provides a multi-language, rules-based approach to matching whether two names refer to the same person, handling variations in formatting, transliteration, cultural usage, and more to determine if names are equivalent with a high degree of confidence.

- **Multiple transliteration variants of foreign names** (e.g., "Mohammed bin Hamad Al Thani" – "Sheikh Mohammed")
- **Nicknames and diminutives** (e.g., "Joseph Robinette Biden Jr." – "Joe Biden") 
- **Common misspellings** (e.g., "Vladimir Vladimirovich Putin" – "Vladimir Putin")
- **Orthographic variations with diacritics** (e.g., "Emmanuel Jean-Michel Frédéric Macron" – "Emmanuel Macron")
- **Tokenization variations** (e.g., "Kim Jong-un" – "Kim Jong Un")
- **Different transliteration standards** (e.g., "Hamad bin Khalifa" – "Hamad ibn Khalifah")
- **Optional name components** (e.g., "Elizabeth Alexandra Mary Windsor" – "Queen Elizabeth II")
- **Name order variations** (e.g., "Jae-in Moon" – "Moon Jae-in")
- **Ethnicity-specific variations** (e.g., "bin" vs "ibn" in Arabic names)
- **Names written in different scripts and languages** (e.g., "Angela Merkel" – "أنجيلا ميركل" – "アンゲラ・メルケル")

## Usage

```python
from human_match import NameMatcher, match_basic

# Simple usage - just get the confidence score
confidence = match_basic("John Smith", "Jon Smith")
print(confidence)  # 0.96

# Advanced usage with full matcher instance
matcher = NameMatcher()

# Match two names
result = matcher.match_names("John Smith", "Jon Smith")
print(result['confidence']) # Confidence: 0.96

# Access components of the result
print(result['name1'].language) # Language.ENGLISH
print(result['name2'].first) # Jon
print(result['name2'].last) # Smith
```

## Supported Languages

- [x] English
- [x] French
- [x] German
- [x] Italian
- [x] Spanish
- [x] Portuguese
- [x] Arabic
- [x] Russian
- [ ] Hindi
- [ ] Bengali
- [ ] Dutch
- [ ] Turkish
- [ ] Greek
- [ ] Polish
- [ ] Urdu
- [ ] Romanian
- [ ] Swedish
- [ ] Norwegian
- [ ] Danish
- [ ] Icelandic
- [ ] Finnish
- [x] Mandarin
- [ ] Japanese
- [ ] Korean
- [ ] Vietnamese
- [ ] Thai
- [ ] Malay
- [ ] Indonesian
- [ ] Filipino
- [ ] Hebrew
- [ ] Farsi

## Theory

The human name matching engine employs a factor model based statistical approach combining phonetic encoding, edit distance metrics, diminutive expansion, particle normalization, and honorific removal across supported languages:

**Phonetic Encoding**: Uses Double Metaphone and Soundex algorithms to generate phonetic representations, enabling matches between names that sound similar but are spelled differently (e.g., "Smith" vs "Smyth"). Arabic names receive specialized phonetic handling.

**Edit Distance**: Primary similarity calculation using Jaro-Winkler distance with fallbacks to Jaro and Levenshtein metrics. For Arabic text, specialized similarity functions handle both Arabic script and romanized variants with cross-script matching.

**Diminutives**: Bidirectional lookup tables map formal names to nicknames (e.g., "Robert" ↔ "Bob", "Francisco" ↔ "Paco"). The system expands both names to all possible variants and finds the best match across all combinations.

**Particles**: Language-specific surname normalization removes particles for comparison while preserving them in output:
- German: von, zu, der, van, de
- French: de, du, des, le, la, les
- Italian: di, del, della, dei, delle
- Spanish: de, del, de la, de los
- Portuguese: da, das, do, dos
- Arabic: al, ibn, bin, abu, abd

**Honorifics**: Systematic removal of titles and honorifics (Dr., Prof., Herr, etc.) with language-specific dictionaries plus common cross-language titles. Special handling prevents over-stripping when particles follow honorifics.

**Composite Factor Scoring**: Adaptive weighted combination of first name (35%), last name (35%), middle name (15%), and phonetic similarity (15%), with dynamic weight adjustment based on component quality and length penalties for significant size differences.

## License

Released under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
