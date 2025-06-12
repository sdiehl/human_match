"""Test cases for English name matching."""

import pytest
from human_match import NameMatcher, Language


class TestEnglishNameMatching:
    """Test English name matching functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = NameMatcher()

    def test_exact_matches(self):
        """Test exact name matches."""
        test_cases = [
            ("John Smith", "John Smith"),
            ("Mary Jane Watson", "Mary Jane Watson"),
            ("Robert Johnson", "Robert Johnson"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= 0.95, f"Failed for {name1} vs {name2}"
            assert result["name1"].language == Language.ENGLISH
            assert result["name2"].language == Language.ENGLISH

    def test_diminutives_matching(self):
        """Test matching with diminutives/nicknames."""
        test_cases = [
            ("Robert Smith", "Bob Smith", 0.85),
            ("William Johnson", "Bill Johnson", 0.85),
            ("Elizabeth Taylor", "Betty Taylor", 0.85),
            ("Richard Brown", "Dick Brown", 0.85),
            ("Margaret Wilson", "Maggie Wilson", 0.85),
            ("Christopher Davis", "Chris Davis", 0.85),
            ("Katherine Miller", "Katie Miller", 0.85),
            ("Benjamin Franklin", "Ben Franklin", 0.85),
            ("Rebecca Jones", "Becky Jones", 0.85),
            ("Alexander Hamilton", "Alex Hamilton", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence, (
                f"Failed for {name1} vs {name2}: {result['confidence']:.3f}"
            )
            assert result["scores"]["first_name"] >= 0.8

    def test_case_insensitive_matching(self):
        """Test case insensitive matching."""
        test_cases = [
            ("john smith", "JOHN SMITH"),
            ("Mary JONES", "mary jones"),
            ("RoBerT WiLsOn", "robert wilson"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= 0.95

    def test_partial_matches(self):
        """Test partial name matches."""
        test_cases = [
            ("John Michael Smith", "John Smith", 0.7),
            ("Mary Elizabeth Jones", "Mary Jones", 0.7),
            ("Robert J. Wilson", "Robert Wilson", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_middle_initial_matching(self):
        """Test matching with middle initials."""
        test_cases = [
            ("John M Smith", "John Michael Smith"),
            ("Mary J Wilson", "Mary Jane Wilson"),
            ("Robert K Johnson", "Robert Kenneth Johnson"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= 0.8
            assert result["scores"]["middle_name"] >= 0.9

    def test_honorifics_removal(self):
        """Test that honorifics are properly removed."""
        test_cases = [
            ("Dr. John Smith", "John Smith"),
            ("Mr. Robert Wilson", "Bob Wilson"),
            ("Prof. Margaret Jones", "Maggie Jones"),
            ("Rev. William Brown", "Bill Brown"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= 0.8

    def test_name_segmentation(self):
        """Test proper name segmentation."""
        test_cases = [
            ("John Michael Smith", ["John", "Michael", "Smith"]),
            ("Mary Elizabeth Jones Jr", ["Mary", "Elizabeth", "Jones"]),
            ("Robert Wilson", ["Robert", "", "Wilson"]),
        ]

        for name, expected in test_cases:
            components = self.matcher.segment_name(name)
            assert components.first == expected[0]
            assert components.middle == expected[1]
            assert components.last == expected[2]

    def test_phonetic_matching(self):
        """Test phonetic matching for similar sounding names."""
        test_cases = [
            ("Smith", "Smyth", 0.7),
            ("Johnson", "Jonson", 0.8),
            ("Catherine", "Katherine", 0.8),
            ("Steven", "Stephen", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence
            assert result["scores"]["phonetic"] >= 0.7

    def test_hyphenated_names(self):
        """Test handling of hyphenated names."""
        test_cases = [
            ("Mary-Jane Watson", "Mary Jane Watson", 0.9),
            ("Jean-Paul Smith", "Jean Paul Smith", 0.9),
            ("Anne-Marie Wilson", "Anne Marie Wilson", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_non_matches(self):
        """Test cases that should not match."""
        test_cases = [
            ("John Smith", "Jane Doe", 0.6),
            ("Robert Wilson", "Michael Johnson", 0.45),
            ("Mary Jones", "Patricia Brown", 0.4),
        ]

        for name1, name2, max_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] <= max_confidence

    def test_gender_neutral_names(self):
        """Test gender-neutral names."""
        test_cases = [
            ("Alex Johnson", "Alexander Johnson"),
            ("Sam Smith", "Samuel Smith"),
            ("Chris Wilson", "Christopher Wilson"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= 0.8

    def test_compound_surnames(self):
        """Test compound surnames."""
        test_cases = [
            ("John Smith-Jones", "John Smith Jones", 0.85),
            ("Mary O'Connor", "Mary OConnor", 0.8),
            ("Robert MacPherson", "Robert McPherson", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_backwards_compatibility(self):
        """Test the legacy match function."""
        from human_match import match

        result = match("Robert Smith", "Bob Smith")
        assert "name1" in result
        assert "name2" in result
        assert "confidence" in result
        assert result["confidence"] >= 0.8
        assert result["name1"]["lang"] == "en"


@pytest.mark.parametrize(
    "name1,name2,expected_min",
    [
        ("Robert Smith", "Bob Smith", 0.85),
        ("Elizabeth Jones", "Betty Jones", 0.85),
        ("William Wilson", "Bill Wilson", 0.85),
        ("Margaret Brown", "Maggie Brown", 0.85),
        ("Christopher Davis", "Chris Davis", 0.88),
    ],
)
def test_parametrized_diminutives(name1, name2, expected_min):
    """Parametrized test for diminutives."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2)
    assert result["confidence"] >= expected_min
