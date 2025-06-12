"""Test cases for Spanish name matching."""

import pytest
from human_match import NameMatcher, Language


class TestSpanishNameMatching:
    """Test Spanish name matching functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.matcher = NameMatcher()

    def test_spanish_language_detection(self) -> None:
        """Test Spanish language detection."""
        spanish_names = [
            "Francisco González",
            "Carlos Rodríguez",
            "Ana Martínez",
            "Miguel Sánchez",
            "Pedro de los Santos",
        ]

        for name in spanish_names:
            components = self.matcher.segment_name(name)
            assert components.language == Language.SPANISH

    def test_spanish_exact_matches(self) -> None:
        """Test exact Spanish name matches."""
        test_cases = [
            ("Carlos García", "Carlos García"),
            ("María González", "María González"),
            ("José de la Cruz", "José de la Cruz"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= 0.95
            assert result["name1"].language == Language.SPANISH

    def test_spanish_diminutives(self) -> None:
        """Test Spanish diminutives matching."""
        test_cases = [
            ("Francisco García", "Paco García", 0.85),
            ("José Rodríguez", "Pepe Rodríguez", 0.85),
            ("Antonio López", "Toni López", 0.85),
            ("Manuel Martínez", "Manu Martínez", 0.85),
            ("Alejandro Sánchez", "Alex Sánchez", 0.85),
            ("María Fernández", "Mari Fernández", 0.85),
            ("Carmen Jiménez", "Carmencita Jiménez", 0.85),
            ("Dolores Ruiz", "Lola Ruiz", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence, (
                f"Failed for {name1} vs {name2}: {result['confidence']:.3f}"
            )

    def test_spanish_particles(self) -> None:
        """Test handling of Spanish particles (de, del, de la, etc.)."""
        test_cases = [
            ("Carlos de la Cruz", "Carlos Cruz", 0.85),
            ("María del Carmen", "María Carmen", 0.85),
            ("José de los Santos", "José Santos", 0.85),
            ("Ana de las Flores", "Ana Flores", 0.85),
            ("Francisco del Río", "Francisco Río", 0.80),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence

    def test_spanish_accents(self) -> None:
        """Test handling of Spanish accents."""
        test_cases = [
            ("José García", "Jose Garcia", 0.9),
            ("María López", "Maria Lopez", 0.9),
            ("Jesús Martínez", "Jesus Martinez", 0.9),
            ("Ángel Rodríguez", "Angel Rodriguez", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_spanish_honorifics(self) -> None:
        """Test Spanish honorifics removal."""
        test_cases = [
            ("Señor Carlos García", "Carlos García"),
            ("Señora María López", "María López"),
            ("Dr. José Martínez", "José Martínez"),
            ("Prof. Ana Rodríguez", "Ana Rodríguez"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= 0.9

    def test_spanish_compound_names(self) -> None:
        """Test Spanish compound/hyphenated names."""
        test_cases = [
            ("María-José García", "María José García", 0.9),
            ("Ana-Belén López", "Ana Belén López", 0.9),
            ("Juan-Carlos Martínez", "Juan Carlos Martínez", 0.9),
            ("José-Luis Rodríguez", "José Luis Rodríguez", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence

    def test_spanish_name_segmentation(self) -> None:
        """Test Spanish name segmentation."""
        test_cases = [
            ("Carlos de García", "Carlos", "", "de García"),
            ("María Elena López", "María", "Elena", "López"),
            ("José Martínez", "José", "", "Martínez"),
            ("Ana de la Cruz", "Ana", "", "de la Cruz"),
        ]

        for name, expected_first, expected_middle, expected_last in test_cases:
            components = self.matcher.segment_name(name, Language.SPANISH)
            assert components.first == expected_first
            assert components.middle == expected_middle
            assert components.last == expected_last

    def test_spanish_surnames_with_particles(self) -> None:
        """Test complex Spanish surnames with particles."""
        test_cases = [
            ("Francisco de San José", "Francisco José", 0.8),
            ("María de la Santa Cruz", "María Cruz", 0.8),
            ("Carlos del Santo Domingo", "Carlos Domingo", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence

    def test_spanish_phonetic_matching(self) -> None:
        """Test phonetic matching for Spanish names."""
        test_cases = [
            ("García", "Garsia", 0.8),
            ("Rodríguez", "Rodriguez", 0.8),
            ("Martínez", "Martinez", 0.8),
            ("González", "Gonzalez", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence

    def test_mixed_spanish_english_matching(self) -> None:
        """Test matching between Spanish and English variants."""
        test_cases = [
            ("José García", "Joseph García", 0.7),
            ("Francisco López", "Francis López", 0.7),
            ("Juan Martínez", "John Martínez", 0.7),
            ("Antonio Rodríguez", "Anthony Rodríguez", 0.7),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_spanish_double_surnames(self) -> None:
        """Test Spanish double surnames."""
        test_cases = [
            ("Carlos García-López", "Carlos García López", 0.9),
            ("María Rodríguez-Martínez", "María Rodríguez Martínez", 0.9),
            ("José Fernández-Sánchez", "José Fernández Sánchez", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence

    def test_spanish_patronymic_endings(self) -> None:
        """Test Spanish patronymic surname endings."""
        test_cases = [
            ("Carlos Rodríguez", "Carlos Rodriguez", 0.9),
            ("María Fernández", "María Fernandez", 0.9),
            ("José Martínez", "José Martinez", 0.9),
            ("Ana González", "Ana Gonzalez", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence

    def test_spanish_regional_variations(self) -> None:
        """Test Spanish regional name variations."""
        test_cases = [
            ("Jesús García", "Chuy García", 0.8),
            ("Ignacio López", "Nacho López", 0.8),
            ("Guillermo Martínez", "Memo Martínez", 0.8),
            ("Enrique Rodríguez", "Quique Rodríguez", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2, language1=Language.SPANISH)
            assert result["confidence"] >= min_confidence


@pytest.mark.parametrize(
    "name1,name2,expected_min",
    [
        ("Francisco García", "Paco García", 0.85),
        ("José Rodríguez", "Pepe Rodríguez", 0.85),
        ("Antonio López", "Toni López", 0.85),
        ("Manuel Martínez", "Manu Martínez", 0.85),
        ("María Fernández", "Mari Fernández", 0.85),
    ],
)
def test_parametrized_spanish_diminutives(
    name1: str, name2: str, expected_min: float
) -> None:
    """Parametrized test for Spanish diminutives."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2, language1=Language.SPANISH)
    assert result["confidence"] >= expected_min
