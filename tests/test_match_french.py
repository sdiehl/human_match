"""Test cases for French name matching."""

import pytest
from human_match import NameMatcher, Language


class TestFrenchNameMatching:
    """Test French name matching functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = NameMatcher()

    def test_french_language_detection(self):
        """Test French language detection."""
        french_names = [
            "Jean-Pierre Dubois",
            "François Mitterrand",
            "Élisabeth Vigée-Lebrun",
            "René Descartes",
            "Pierre-Alexandre Dupont",
        ]

        for name in french_names:
            components = self.matcher.segment_name(name)
            assert components.language == Language.FRENCH

    def test_french_exact_matches(self):
        """Test exact French name matches."""
        test_cases = [
            ("Jean Dupont", "Jean Dupont"),
            ("Marie-Claire Dubois", "Marie-Claire Dubois"),
            ("François de la Rochefoucauld", "François de la Rochefoucauld"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.FRENCH)
            assert result["confidence"] >= 0.95
            assert result["name1"].language == Language.FRENCH

    def test_french_diminutives(self):
        """Test French diminutives matching."""
        test_cases = [
            ("Alexandre Dubois", "Alex Dubois", 0.85),
            ("Benjamin Martin", "Ben Martin", 0.85),
            ("François Durand", "Fran Durand", 0.80),
            ("Nicolas Bernard", "Nico Bernard", 0.85),
            ("Sébastien Moreau", "Seb Moreau", 0.85),
            ("Élisabeth Leclerc", "Lise Leclerc", 0.80),
            ("Marie-Christine Simon", "Marie Simon", 0.70),
            ("Jean-Pierre Robert", "Pierre Robert", 0.70),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.FRENCH)
            assert result["confidence"] >= min_confidence, (
                f"Failed for {name1} vs {name2}: {result['confidence']:.3f}"
            )

    def test_french_particles(self):
        """Test handling of French particles (de, du, des, le, la)."""
        test_cases = [
            ("Marie de Montpellier", "Marie Montpellier", 0.85),
            ("Jean du Pont", "Jean Pont", 0.85),
            ("Pierre des Jardins", "Pierre Jardins", 0.85),
            ("Claire le Blanc", "Claire Blanc", 0.85),
            ("Anne la Rouge", "Anne Rouge", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.FRENCH)
            assert result["confidence"] >= min_confidence

    def test_french_accented_characters(self):
        """Test handling of French accented characters."""
        test_cases = [
            ("François Müller", "Francois Muller", 0.9),
            ("José García", "Jose Garcia", 0.9),
            ("Élisabeth Thévenot", "Elisabeth Thevenot", 0.9),
            ("René Côté", "Rene Cote", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_french_honorifics(self):
        """Test French honorifics removal."""
        test_cases = [
            ("M. Jean Dupont", "Jean Dupont"),
            ("Mme Marie Martin", "Marie Martin"),
            ("Dr François Dubois", "François Dubois"),
            ("Prof. Pierre Moreau", "Pierre Moreau"),
            ("Mlle Élisabeth Bernard", "Élisabeth Bernard"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.FRENCH)
            assert result["confidence"] >= 0.95

    def test_french_compound_names(self):
        """Test French compound/hyphenated names."""
        test_cases = [
            ("Jean-Pierre Dubois", "Jean Pierre Dubois", 0.9),
            ("Marie-Claire Martin", "Marie Claire Martin", 0.9),
            ("Anne-Sophie Moreau", "Anne Sophie Moreau", 0.9),
            ("Jean-Luc Bernard", "Jean Luc Bernard", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.FRENCH)
            assert result["confidence"] >= min_confidence

    def test_french_name_segmentation(self):
        """Test French name segmentation."""
        test_cases = [
            ("Jean-Pierre de Montpellier", "Jean-Pierre", "", "de Montpellier"),
            ("Marie Claire Dubois", "Marie", "Claire", "Dubois"),
            ("François Mitterrand", "François", "", "Mitterrand"),
            ("Général de Gaulle", "Général", "", "de Gaulle"),
        ]

        for name, expected_first, expected_middle, expected_last in test_cases:
            components = self.matcher.segment_name(name, Language.FRENCH)
            assert components.first == expected_first
            assert components.middle == expected_middle
            assert components.last == expected_last

    def test_mixed_french_english_matching(self):
        """Test matching between French and English variants."""
        test_cases = [
            ("Jean Dubois", "John Dubois", 0.7),
            ("Pierre Martin", "Peter Martin", 0.7),
            ("Marie Bernard", "Mary Bernard", 0.7),
            ("François Moreau", "Francis Moreau", 0.7),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_french_phonetic_matching(self):
        """Test phonetic matching for French names."""
        test_cases = [
            ("Laurent", "Lorent", 0.7),
            ("Thierry", "Tierry", 0.8),
            ("Gérard", "Gerard", 0.9),
            ("Cécile", "Cecile", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.FRENCH)
            assert result["confidence"] >= min_confidence

    def test_french_surnames_with_apostrophes(self):
        """Test French surnames with apostrophes."""
        test_cases = [
            ("Jean d'Arc", "Jean dArc", 0.85),
            ("Marie l'Ange", "Marie lAnge", 0.85),
            ("Pierre d'Olivier", "Pierre dOlivier", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.FRENCH)
            assert result["confidence"] >= min_confidence


@pytest.mark.parametrize(
    "name1,name2,expected_min",
    [
        ("Alexandre Martin", "Alex Martin", 0.85),
        ("Benjamin Dubois", "Ben Dubois", 0.85),
        ("Nicolas Bernard", "Nico Bernard", 0.85),
        ("Sébastien Moreau", "Seb Moreau", 0.85),
        ("Élisabeth Robert", "Lise Robert", 0.80),
    ],
)
def test_parametrized_french_diminutives(name1, name2, expected_min):
    """Parametrized test for French diminutives."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2, language1=Language.FRENCH)
    assert result["confidence"] >= expected_min
