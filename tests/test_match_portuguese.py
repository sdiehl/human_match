"""Test cases for Portuguese name matching."""

import pytest
from human_match import NameMatcher, Language


class TestPortugueseNameMatching:
    """Test Portuguese name matching functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.matcher = NameMatcher()

    def test_portuguese_language_detection(self) -> None:
        """Test Portuguese language detection."""
        portuguese_names = [
            "João Silva",
            "Maria da Costa",
            "António dos Santos",
            "Gonçalo Ferreira",
            "Inês Rodrigues",
            "Tiago Santos",
        ]

        for name in portuguese_names:
            components = self.matcher.segment_name(name)
            assert components.language == Language.PORTUGUESE

    def test_portuguese_exact_matches(self) -> None:
        """Test exact Portuguese name matches."""
        test_cases = [
            ("João Silva", "João Silva"),
            ("Maria Santos", "Maria Santos"),
            ("António Costa", "António Costa"),
            ("Ana Oliveira", "Ana Oliveira"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= 0.95
            assert result["name1"].language == Language.PORTUGUESE

    def test_portuguese_diminutives(self) -> None:
        """Test Portuguese diminutives matching."""
        test_cases = [
            ("Francisco Silva", "Chico Silva", 0.85),
            ("António Santos", "Toninho Santos", 0.85),
            ("João Costa", "Joãozinho Costa", 0.85),
            ("José Oliveira", "Zé Oliveira", 0.85),
            ("Manuel Rodrigues", "Manel Rodrigues", 0.85),
            ("Pedro Ferreira", "Pedrinho Ferreira", 0.85),
            ("Carlos Pereira", "Carlinhos Pereira", 0.85),
            ("Paulo Santos", "Paulinho Santos", 0.85),
            ("Fernando Costa", "Nando Costa", 0.85),
            ("Ricardo Silva", "Ricky Silva", 0.85),
            ("Roberto Oliveira", "Beto Oliveira", 0.85),
            ("Maria Santos", "Mariazinha Santos", 0.85),
            ("Ana Costa", "Aninha Costa", 0.85),
            ("Isabel Silva", "Isa Silva", 0.85),
            ("Catarina Rodrigues", "Cata Rodrigues", 0.85),
            ("Beatriz Santos", "Bia Santos", 0.85),
            ("Alexandre Costa", "Alex Costa", 0.85),
            ("Guilherme Silva", "Gui Silva", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= min_confidence, (
                f"Failed for {name1} vs {name2}: {result['confidence']:.3f}"
            )

    def test_portuguese_particles(self) -> None:
        """Test handling of Portuguese particles (da, das, de, do, dos, etc.)."""
        test_cases = [
            ("João da Silva", "João Silva", 0.85),
            ("Maria das Neves", "Maria Neves", 0.85),
            ("António de Oliveira", "António Oliveira", 0.85),
            ("Ana do Carmo", "Ana Carmo", 0.85),
            ("José dos Santos", "José Santos", 0.85),
            ("Francisco de Sousa", "Francisco Sousa", 0.85),
            ("Pedro da Costa", "Pedro Costa", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= min_confidence

    def test_portuguese_accents(self) -> None:
        """Test handling of Portuguese accents and diacritics."""
        test_cases = [
            ("João Silva", "Joao Silva", 0.9),
            ("José Santos", "Jose Santos", 0.9),
            ("António Costa", "Antonio Costa", 0.9),
            ("Conceição Oliveira", "Conceicao Oliveira", 0.9),
            ("Inês Rodrigues", "Ines Rodrigues", 0.9),
            ("André Santos", "Andre Santos", 0.9),
            ("Vítor Costa", "Vitor Costa", 0.9),
            ("Sónia Silva", "Sonia Silva", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_portuguese_honorifics(self) -> None:
        """Test Portuguese honorifics removal."""
        test_cases = [
            ("Sr. João Silva", "João Silva"),
            ("Sra. Maria Santos", "Maria Santos"),
            ("Dr. António Costa", "António Costa"),
            ("Dra. Ana Oliveira", "Ana Oliveira"),
            ("Prof. José Rodrigues", "José Rodrigues"),
            ("Eng. Pedro Santos", "Pedro Santos"),
        ]

        for name1, name2 in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= 0.9

    def test_portuguese_compound_names(self) -> None:
        """Test Portuguese compound/hyphenated names."""
        test_cases = [
            ("João-Carlos Silva", "João Carlos Silva", 0.9),
            ("Maria-José Santos", "Maria José Santos", 0.9),
            ("Ana-Paula Costa", "Ana Paula Costa", 0.9),
            ("José-António Oliveira", "José António Oliveira", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= min_confidence

    def test_portuguese_name_segmentation(self) -> None:
        """Test Portuguese name segmentation."""
        test_cases = [
            ("João Carlos Silva", "João", "Carlos", "Silva"),
            ("Maria da Conceição Santos", "Maria", "", "da Conceição Santos"),
            ("António José de Oliveira", "António", "José", "de Oliveira"),
            ("Ana Paula Costa", "Ana", "Paula", "Costa"),
        ]

        for name, expected_first, expected_middle, expected_last in test_cases:
            components = self.matcher.segment_name(name, Language.PORTUGUESE)
            assert components.first == expected_first
            assert components.middle == expected_middle
            assert components.last == expected_last

    def test_portuguese_surnames_with_particles(self) -> None:
        """Test complex Portuguese surnames with particles."""
        test_cases = [
            ("João da Silva Santos", "João Santos", 0.7),
            ("Maria das Dores Oliveira", "Maria Oliveira", 0.7),
            ("António de Sousa e Silva", "António Silva", 0.7),
            ("Ana do Carmo Rodrigues", "Ana Rodrigues", 0.7),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= min_confidence

    def test_portuguese_phonetic_matching(self) -> None:
        """Test phonetic matching for Portuguese names."""
        test_cases = [
            ("Silva", "Silveira", 0.7),
            ("Santos", "Santas", 0.8),
            ("Oliveira", "Oliveyra", 0.8),
            ("Rodrigues", "Rodriges", 0.8),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= min_confidence

    def test_mixed_portuguese_spanish_matching(self) -> None:
        """Test matching between Portuguese and Spanish variants."""
        test_cases = [
            ("João Silva", "Juan Silva", 0.7),
            ("José Santos", "José Santos", 0.95),  # Same in both languages
            ("António Costa", "Antonio Costa", 0.9),  # Just accent difference
            ("Maria Oliveira", "María Oliveira", 0.9),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_portuguese_double_surnames(self) -> None:
        """Test Portuguese double surnames."""
        test_cases = [
            ("João Silva Santos", "João Silva Santos", 0.95),
            ("Maria Costa Rodrigues", "Maria Costa Rodrigues", 0.95),
            ("António Oliveira Pereira", "António Oliveira Pereira", 0.95),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(
                name1, name2, language1=Language.PORTUGUESE
            )
            assert result["confidence"] >= min_confidence

    def test_brazilian_vs_portuguese_names(self) -> None:
        """Test Brazilian vs European Portuguese name variations."""
        test_cases = [
            ("Antônio Silva", "António Silva", 0.85),  # Different accent style
            ("Luiz Santos", "Luís Santos", 0.85),
            ("Thiago Costa", "Tiago Costa", 0.8),
            ("Fabio Oliveira", "Fábio Oliveira", 0.85),
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence

    def test_portuguese_cross_language_matching(self) -> None:
        """Test cross-language matching with Portuguese names."""
        test_cases = [
            ("José Silva", "Joseph Silva", 0.7),  # Portuguese to English
            ("João Santos", "Jean Santos", 0.7),  # Portuguese to French
            ("Pedro Costa", "Peter Costa", 0.7),  # Portuguese to English
            ("Maria Oliveira", "Marie Oliveira", 0.7),  # Portuguese to French
        ]

        for name1, name2, min_confidence in test_cases:
            result = self.matcher.match_names(name1, name2)
            assert result["confidence"] >= min_confidence


@pytest.mark.parametrize(
    "name1,name2,expected_min",
    [
        ("Francisco Silva", "Chico Silva", 0.85),
        ("António Santos", "Toninho Santos", 0.85),
        ("João Costa", "Joãozinho Costa", 0.85),
        ("José Oliveira", "Zé Oliveira", 0.85),
        ("Manuel Rodrigues", "Manel Rodrigues", 0.85),
        ("Maria Santos", "Mariazinha Santos", 0.85),
        ("Ana Costa", "Aninha Costa", 0.85),
        ("Isabel Silva", "Isa Silva", 0.85),
    ],
)
def test_parametrized_portuguese_diminutives(
    name1: str, name2: str, expected_min: float
) -> None:
    """Parametrized test for Portuguese diminutives."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2, language1=Language.PORTUGUESE)
    assert result["confidence"] >= expected_min
