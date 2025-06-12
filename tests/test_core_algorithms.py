"""Test cases for core name matching algorithms."""

import pytest
from human_match import NameMatcher, Language


class TestCoreAlgorithms:
    """Test core name matching algorithms."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.matcher = NameMatcher()

    def test_language_detection(self) -> None:
        """Test language detection algorithm."""
        test_cases = [
            ("John Smith", Language.ENGLISH),
            ("Hans von Mueller", Language.GERMAN),  # Clear German with particles
            ("François Mitterrand", Language.FRENCH),  # Clear French with accents
            ("Wolfgang Schröder", Language.GERMAN),  # Clear German with umlauts
            ("Elisabeth Kühn", Language.GERMAN),  # Clear German with umlauts
            ("Jean-Pierre Dubois", Language.FRENCH),  # Clear French with compound name
            ("Robert Johnson", Language.ENGLISH),
            ("João Silva", Language.PORTUGUESE),  # Portuguese with accents
            ("Muhammad Ahmed", Language.ARABIC),  # Arabic romanized
            ("محمد أحمد", Language.ARABIC),  # Arabic script
            ("António dos Santos", Language.PORTUGUESE),  # Portuguese with particles
        ]

        for name, expected_lang in test_cases:
            detected_lang = self.matcher.detect_language(name)
            assert detected_lang == expected_lang, f"Failed for {name}"

    def test_name_segmentation(self) -> None:
        """Test name segmentation algorithm."""
        test_cases = [
            ("John Michael Smith", "John", "Michael", "Smith"),
            ("Dr. Robert Wilson", "Robert", "", "Wilson"),
            ("Mary-Jane Watson", "Mary-Jane", "", "Watson"),
            ("Jean-Pierre de Montpellier", "Jean-Pierre", "", "de Montpellier"),
            ("Hans von Mueller", "Hans", "", "von Mueller"),
        ]

        for name, expected_first, expected_middle, expected_last in test_cases:
            components = self.matcher.segment_name(name)
            assert components.first == expected_first
            assert components.middle == expected_middle
            assert components.last == expected_last
            assert components.original == name

    def test_honorifics_removal(self) -> None:
        """Test honorifics removal across languages."""
        test_cases = [
            ("Dr. John Smith", Language.ENGLISH, "John Smith"),
            ("M. Jean Dupont", Language.FRENCH, "Jean Dupont"),
            ("Herr Hans Schmidt", Language.GERMAN, "Hans Schmidt"),
            ("Prof. Mary Wilson", Language.ENGLISH, "Mary Wilson"),
            ("Mme Marie Martin", Language.FRENCH, "Marie Martin"),
            ("Frau Elisabeth Mueller", Language.GERMAN, "Elisabeth Mueller"),
        ]

        for name, language, expected in test_cases:
            cleaned = self.matcher._strip_honorifics(name, language)
            assert cleaned == expected

    def test_diminutives_expansion(self) -> None:
        """Test diminutives expansion."""
        test_cases = [
            ("robert", Language.ENGLISH, ["robert", "bob", "rob", "bert"]),
            ("alex", Language.FRENCH, ["alex", "alexandre"]),
            ("fritz", Language.GERMAN, ["fritz", "friedrich"]),
        ]

        for name, language, expected_variants in test_cases:
            variants = self.matcher.expand_diminutives(name, language)
            # Check that all expected variants are present (order may vary)
            for variant in expected_variants:
                assert variant in variants, f"Missing variant {variant} for {name}"

    def test_phonetic_encoding(self) -> None:
        """Test phonetic encoding algorithms."""
        test_cases = [
            ("Smith", "metaphone"),
            ("Johnson", "metaphone"),
            ("Brown", "soundex"),
            ("Wilson", "soundex"),
        ]

        for name, algorithm in test_cases:
            encoding = self.matcher.phonetic_encoding(name, algorithm)
            assert len(encoding) > 0
            assert isinstance(encoding, str)

    def test_string_distance_algorithms(self) -> None:
        """Test string distance algorithms."""
        test_cases = [
            ("Smith", "Smith", "jaro_winkler", 1.0),
            ("Smith", "Smyth", "jaro_winkler", 0.8),
            ("Johnson", "Jonson", "jaro_winkler", 0.8),
            ("identical", "identical", "levenshtein", 1.0),
            ("", "", "jaro_winkler", 1.0),
        ]

        for s1, s2, algorithm, min_score in test_cases:
            score = self.matcher.calculate_distance(s1, s2, algorithm)
            assert score >= min_score, f"Failed for {s1} vs {s2} with {algorithm}"
            assert 0.0 <= score <= 1.0

    def test_phonetic_comparison(self) -> None:
        """Test phonetic comparison of names."""
        test_cases = [
            ("Smith", "Smyth", 0.7),
            ("Johnson", "Jonson", 0.8),
            ("Catherine", "Katherine", 0.8),
            ("Stephen", "Steven", 0.8),
        ]

        for name1, name2, min_score in test_cases:
            score = self.matcher._compare_phonetic(name1, name2)
            assert score >= min_score

    def test_middle_name_comparison(self) -> None:
        """Test middle name comparison with initials."""
        test_cases = [
            ("Michael", "Michael", 1.0),
            ("M", "Michael", 1.0),
            ("Michael", "M", 1.0),
            ("John", "J", 1.0),
            ("", "", 0.5),
            ("Michael", "", 0.0),
            ("M", "John", 0.0),
        ]

        for middle1, middle2, expected_score in test_cases:
            score = self.matcher._compare_middle_names(middle1, middle2)
            assert score == expected_score

    def test_surname_normalization(self) -> None:
        """Test surname normalization for different languages."""
        test_cases = [
            ("von Mueller", Language.GERMAN, "mueller"),
            ("de Montpellier", Language.FRENCH, "montpellier"),
            ("O'Connor", Language.ENGLISH, "o'connor"),
            ("van der Berg", Language.GERMAN, "berg"),
            ("du Pont", Language.FRENCH, "pont"),
        ]

        for surname, language, expected in test_cases:
            normalized = self.matcher._normalize_surname(surname, language)
            assert normalized == expected

    def test_cross_language_matching(self) -> None:
        """Test matching across different languages."""
        test_cases = [
            ("Jean Dubois", "John Dubois", 0.7),
            ("Pierre Martin", "Peter Martin", 0.7),
            ("Johannes Mueller", "John Mueller", 0.7),
            ("Wilhelm Weber", "William Weber", 0.7),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_score_components(self) -> None:
        """Test that all score components are computed."""
        result = self.matcher.match_names("Robert Smith", "Bob Smith")

        required_scores = [
            "first_name",
            "last_name",
            "middle_name",
            "phonetic",
            "composite",
            "length_penalty",
        ]

        for component in required_scores:
            assert component in result["scores"]
            assert 0.0 <= result["scores"][component] <= 1.0

    def test_empty_name_handling(self) -> None:
        """Test handling of empty or malformed names."""
        test_cases = [
            ("", "John Smith"),
            ("John Smith", ""),
            ("", ""),
            ("   ", "John Smith"),
            ("John", ""),
        ]

        for name1, name2 in test_cases:
            # Should not raise an exception
            result = self.matcher.match_names(name1, name2)
            assert "confidence" in result
            assert result["confidence"] >= 0.0

    def test_unicode_handling(self) -> None:
        """Test proper Unicode handling."""
        test_cases = [
            ("François Müller", "Francois Mueller", 0.83),
            ("José García", "Jose Garcia", 0.9),
            ("Björn Åström", "Bjorn Astrom", 0.83),
            ("Zoë Smith", "Zoe Smith", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_case_sensitivity(self) -> None:
        """Test case insensitive matching."""
        test_cases = [
            ("JOHN SMITH", "john smith", 0.92),
            ("Mary JONES", "mary jones", 0.92),
            ("RoBerT WiLsOn", "robert wilson", 0.92),
        ]

        for name1, name2, min_score in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_score


@pytest.mark.parametrize("algorithm", ["jaro_winkler", "jaro", "levenshtein"])
def test_distance_algorithms(algorithm: str) -> None:
    """Test different distance algorithms."""
    matcher = NameMatcher()

    # Test identical strings
    score = matcher.calculate_distance("test", "test", algorithm)
    assert score == 1.0

    # Test completely different strings
    score = matcher.calculate_distance("abc", "xyz", algorithm)
    assert score < 0.5

    # Test similar strings
    score = matcher.calculate_distance("smith", "smyth", algorithm)
    assert 0.5 < score < 1.0


@pytest.mark.parametrize("encoding", ["metaphone", "soundex"])
def test_phonetic_algorithms(encoding: str) -> None:
    """Test different phonetic algorithms."""
    matcher = NameMatcher()

    # Test that encoding returns a string
    result = matcher.phonetic_encoding("Smith", encoding)
    assert isinstance(result, str)
    assert len(result) > 0

    # Test that similar sounding names have similar encodings
    enc1 = matcher.phonetic_encoding("Smith", encoding)
    enc2 = matcher.phonetic_encoding("Smyth", encoding)

    # They should either be identical or similar
    if enc1 != enc2:
        similarity = matcher.calculate_distance(enc1, enc2)
        assert similarity > 0.5
