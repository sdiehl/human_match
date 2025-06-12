"""Test cases for Italian name matching."""

import pytest
from human_match import NameMatcher, Language


class TestItalianNameMatching:
    """Test Italian name matching functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.matcher = NameMatcher()

    def test_italian_language_detection(self) -> None:
        """Test Italian language detection."""
        italian_names = [
            "Marco di Rossi",
            "Francesco della Valle",
            "Giuseppe Bianchi",
            "Maria Rossi",
            "Alessandro del Monte",
        ]

        for name in italian_names:
            components = self.matcher.segment_name(name)
            assert components.language == Language.ITALIAN

    def test_italian_exact_matches(self) -> None:
        """Test exact Italian name matches."""
        test_cases = [
            ("Marco Rossi", "Marco Rossi"),
            ("Francesco Bianchi", "Francesco Bianchi"),
            ("Maria della Valle", "Maria della Valle"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= 0.95
            assert result["name1"].language == Language.ITALIAN

    def test_italian_diminutives(self) -> None:
        """Test Italian diminutives matching."""
        test_cases = [
            ("Francesco Rossi", "Franco Rossi", 0.85),
            ("Alessandro Bianchi", "Alex Bianchi", 0.85),
            ("Giuseppe Romano", "Beppe Romano", 0.85),
            ("Giovanni Ferrari", "Gianni Ferrari", 0.85),
            ("Roberto Marino", "Roby Marino", 0.85),
            ("Elisabetta Conti", "Lisa Conti", 0.85),
            ("Francesca Ricci", "Francy Ricci", 0.85),
            ("Valentina Greco", "Vale Greco", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= min_confidence, (
                f"Failed for {name1} vs {name2}: {result['confidence']:.3f}"
            )

    def test_italian_particles(self) -> None:
        """Test handling of Italian particles (di, del, della, etc.)."""
        test_cases = [
            ("Marco di Rossi", "Marco Rossi", 0.85),
            ("Francesco del Monte", "Francesco Monte", 0.85),
            ("Maria della Valle", "Maria Valle", 0.85),
            ("Giuseppe dei Fiori", "Giuseppe Fiori", 0.85),
            ("Antonio dalle Alpi", "Antonio Alpi", 0.80),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= min_confidence

    def test_italian_accents(self) -> None:
        """Test handling of Italian accents."""
        test_cases = [
            ("José Martínez", "Jose Martinez", 0.9),
            ("André Müller", "Andre Muller", 0.9),
            ("François Dubois", "Francois Dubois", 0.9),
            ("Nicolò Bianchi", "Nicolo Bianchi", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_italian_honorifics(self) -> None:
        """Test Italian honorifics removal."""
        test_cases = [
            ("Signore Marco Rossi", "Marco Rossi"),
            ("Signora Maria Bianchi", "Maria Bianchi"),
            ("Dott. Francesco Romano", "Francesco Romano"),
            ("Prof. Giuseppe Ferrari", "Giuseppe Ferrari"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= 0.9

    def test_italian_compound_names(self) -> None:
        """Test Italian compound/hyphenated names."""
        test_cases = [
            ("Maria-Luisa Rossi", "Maria Luisa Rossi", 0.9),
            ("Anna-Maria Bianchi", "Anna Maria Bianchi", 0.9),
            ("Gian-Carlo Romano", "Gian Carlo Romano", 0.9),
            ("Pier-Luigi Ferrari", "Pier Luigi Ferrari", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= min_confidence

    def test_italian_name_segmentation(self) -> None:
        """Test Italian name segmentation."""
        test_cases = [
            ("Marco di Rossi", "Marco", "", "di Rossi"),
            ("Francesco Antonio Bianchi", "Francesco", "Antonio", "Bianchi"),
            ("Maria Romano", "Maria", "", "Romano"),
            ("Giuseppe della Valle", "Giuseppe", "", "della Valle"),
        ]

        for name, expected_first, expected_middle, expected_last in test_cases:
            components = self.matcher.segment_name(name, Language.ITALIAN)
            assert components.first == expected_first
            assert components.middle == expected_middle
            assert components.last == expected_last

    def test_italian_surnames_with_particles(self) -> None:
        """Test complex Italian surnames with particles."""
        test_cases = [
            ("Francesco di San Giovanni", "Francesco Giovanni", 0.8),
            ("Marco della Santa Maria", "Marco Maria", 0.8),
            ("Giuseppe del Santo Spirito", "Giuseppe Spirito", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= min_confidence

    def test_italian_phonetic_matching(self) -> None:
        """Test phonetic matching for Italian names."""
        test_cases = [
            ("Rossi", "Rosi", 0.8),
            ("Bianchi", "Bianki", 0.8),
            ("Ferrari", "Ferari", 0.8),
            ("Romano", "Romanu", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= min_confidence

    def test_mixed_italian_english_matching(self) -> None:
        """Test matching between Italian and English variants."""
        test_cases = [
            ("Francesco Rossi", "Francis Rossi", 0.7),
            ("Giuseppe Bianchi", "Joseph Bianchi", 0.7),
            ("Giovanni Romano", "John Romano", 0.7),
            ("Antonio Ferrari", "Anthony Ferrari", 0.7),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_italian_double_surnames(self) -> None:
        """Test Italian double surnames."""
        test_cases = [
            ("Marco Rossi-Bianchi", "Marco Rossi Bianchi", 0.9),
            ("Maria Ferrari-Romano", "Maria Ferrari Romano", 0.9),
            ("Giuseppe Conti-Greco", "Giuseppe Conti Greco", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.ITALIAN)
            assert result["confidence"] >= min_confidence


@pytest.mark.parametrize(
    "name1,name2,expected_min",
    [
        ("Francesco Rossi", "Franco Rossi", 0.85),
        ("Alessandro Bianchi", "Alex Bianchi", 0.85),
        ("Giuseppe Romano", "Beppe Romano", 0.85),
        ("Giovanni Ferrari", "Gianni Ferrari", 0.85),
        ("Elisabetta Conti", "Lisa Conti", 0.85),
    ],
)
def test_parametrized_italian_diminutives(
    name1: str, name2: str, expected_min: float
) -> None:
    """Parametrized test for Italian diminutives."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2, language1=Language.ITALIAN)
    assert result["confidence"] >= expected_min
