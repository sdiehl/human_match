"""Test cases for German name matching."""

import pytest
from human_match import NameMatcher, Language


class TestGermanNameMatching:
    """Test German name matching functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.matcher = NameMatcher()

    def test_german_language_detection(self) -> None:
        """Test German language detection."""
        german_names = [
            "Hans-Georg von Mueller",
            "Friedrich Schmidt",
            "Günther Müller",
            "Elisabeth Kühn",
            "Wolfgang Schröder",
        ]

        for name in german_names:
            components = self.matcher.segment_name(name)
            assert components.language == Language.GERMAN

    def test_german_exact_matches(self) -> None:
        """Test exact German name matches."""
        test_cases = [
            ("Hans Schmidt", "Hans Schmidt"),
            ("Friedrich Mueller", "Friedrich Mueller"),
            ("Elisabeth von Berg", "Elisabeth von Berg"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= 0.95
            assert result["name1"].language == Language.GERMAN

    def test_german_diminutives(self) -> None:
        """Test German diminutives matching."""
        test_cases = [
            ("Friedrich Schmidt", "Fritz Schmidt", 0.85),
            ("Johannes Mueller", "Hans Mueller", 0.85),
            ("Heinrich Weber", "Heinz Weber", 0.85),
            ("Elisabeth Schneider", "Lisa Schneider", 0.85),
            ("Sebastian Fischer", "Basti Fischer", 0.85),
            ("Maximilian Bauer", "Max Bauer", 0.85),
            ("Christina Wagner", "Chris Wagner", 0.85),
            ("Alexander Koch", "Alex Koch", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= min_confidence, (
                f"Failed for {name1} vs {name2}: {result['confidence']:.3f}"
            )

    def test_german_particles(self) -> None:
        """Test handling of German particles (von, zu, der, etc.)."""
        test_cases = [
            ("Hans von Mueller", "Hans Mueller", 0.85),
            ("Friedrich zu Berg", "Friedrich Berg", 0.85),
            ("Elisabeth der Große", "Elisabeth Große", 0.85),
            ("Wolfgang van der Berg", "Wolfgang Berg", 0.80),
            ("Karl am See", "Karl See", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= min_confidence

    def test_german_umlauts(self) -> None:
        """Test handling of German umlauts."""
        test_cases = [
            ("Günther Müller", "Guenther Mueller", 0.9),
            ("Jürgen Schäfer", "Juergen Schaefer", 0.9),
            ("Björn Höfer", "Bjoern Hoefer", 0.9),
            ("Käthe Möller", "Kaethe Moeller", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_german_honorifics(self) -> None:
        """Test German honorifics removal."""
        test_cases = [
            ("Herr Hans Schmidt", "Hans Schmidt"),
            ("Frau Elisabeth Mueller", "Elisabeth Mueller"),
            ("Dr. Friedrich Weber", "Friedrich Weber"),
            ("Prof. Wolfgang Schneider", "Wolfgang Schneider"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= 0.95

    def test_german_compound_names(self) -> None:
        """Test German compound/hyphenated names."""
        test_cases = [
            ("Hans-Georg Schmidt", "Hans Georg Schmidt", 0.9),
            ("Marie-Luise Mueller", "Marie Luise Mueller", 0.9),
            ("Karl-Heinz Weber", "Karl Heinz Weber", 0.9),
            ("Anna-Maria Fischer", "Anna Maria Fischer", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= min_confidence

    def test_german_name_segmentation(self) -> None:
        """Test German name segmentation."""
        test_cases = [
            ("Hans-Georg von Mueller", "Hans-Georg", "", "von Mueller"),
            ("Friedrich Wilhelm Schmidt", "Friedrich", "Wilhelm", "Schmidt"),
            ("Elisabeth Weber", "Elisabeth", "", "Weber"),
            ("Herr von Berg", "Herr", "", "von Berg"),
        ]

        for name, expected_first, expected_middle, expected_last in test_cases:
            components = self.matcher.segment_name(name, Language.GERMAN)
            assert components.first == expected_first
            assert components.middle == expected_middle
            assert components.last == expected_last

    def test_german_surnames_with_particles(self) -> None:
        """Test complex German surnames with particles."""
        test_cases = [
            ("Friedrich von und zu Liechtenstein", "Friedrich Liechtenstein", 0.8),
            ("Hans von der Leyen", "Hans Leyen", 0.85),
            ("Elisabeth zu Guttenberg", "Elisabeth Guttenberg", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= min_confidence

    def test_german_phonetic_matching(self) -> None:
        """Test phonetic matching for German names."""
        test_cases = [
            ("Schmidt", "Schmitt", 0.8),
            ("Mueller", "Müller", 0.9),
            ("Weber", "Waber", 0.8),
            ("Fischer", "Fisher", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= min_confidence

    def test_mixed_german_english_matching(self) -> None:
        """Test matching between German and English variants."""
        test_cases = [
            ("Johannes Mueller", "John Mueller", 0.7),
            ("Friedrich Schmidt", "Frederick Schmidt", 0.7),
            ("Wilhelm Weber", "William Weber", 0.7),
            ("Heinrich Fischer", "Henry Fischer", 0.7),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_german_double_surnames(self) -> None:
        """Test German double surnames."""
        test_cases = [
            ("Hans Mueller-Schmidt", "Hans Mueller Schmidt", 0.9),
            ("Elisabeth Weber-Fischer", "Elisabeth Weber Fischer", 0.9),
            ("Friedrich Schneider-Koch", "Friedrich Schneider Koch", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.GERMAN)
            assert result["confidence"] >= min_confidence


@pytest.mark.parametrize(
    "name1,name2,expected_min",
    [
        ("Friedrich Schmidt", "Fritz Schmidt", 0.85),
        ("Johannes Mueller", "Hans Mueller", 0.85),
        ("Heinrich Weber", "Heinz Weber", 0.85),
        ("Sebastian Fischer", "Basti Fischer", 0.85),
        ("Elisabeth Schneider", "Lisa Schneider", 0.85),
    ],
)
def test_parametrized_german_diminutives(
    name1: str, name2: str, expected_min: float
) -> None:
    """Parametrized test for German diminutives."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2, language1=Language.GERMAN)
    assert result["confidence"] >= expected_min
