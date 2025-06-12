# Human Name Matching Engine

Matching human names is a complex problem. This library provides a multi-language, rules-based approach to matching whether two human names are the same. For example, your passport might read "Mr Robert A. Smith" but your ticket might read "Bob Smith," yet they are highly likely the same name in English. Each language has its own set of rules for matching names, and this library provides a multi-language approach to testing for name similarity.

The library handles these variations across different languages and writing systems. For instance, in Chinese, a name like 王伟 (romanized as Wáng Wěi) might be written as Wei Wang in a Western context, reversing the family and given names.

Similarly, in Russian, a man formally named Александр Петров (Aleksandr Petrov) is commonly called Саша Петров (Sasha Petrov), where Sasha is a standard diminutive for Aleksandr. This library can identify these as probable matches.

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