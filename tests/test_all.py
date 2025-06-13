"""Test cases for verifying name matches from CSV file."""

import csv
from typing import List, Tuple
import pytest
from human_match import NameMatcher


def load_test_cases() -> List[Tuple[str, str]]:
    """Load test cases from CSV file."""
    test_cases = []
    with open("tests/similar_names.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append((row["name1"], row["name2"]))
    return test_cases


def load_advanced_test_cases() -> List[Tuple[str, str]]:
    """Load advanced test cases from CSV file."""
    test_cases = []
    with open("tests/advanced.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append((row["name1"], row["name2"]))
    return test_cases


@pytest.mark.parametrize("name1,name2", load_test_cases())
def test_name_matches(name1: str, name2: str) -> None:
    """Test that name pairs from CSV match with high similarity."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2)

    assert result["confidence"] > 0.75, (
        f"Match confidence for '{name1}' vs '{name2}' "
        f"was {result['confidence']:.3f}, expected > 0.75"
    )


@pytest.mark.parametrize("name1,name2", load_advanced_test_cases())
def test_advanced_name_matches(name1: str, name2: str) -> None:
    """Test advanced name matching scenarios including:
    - Multiple transliteration variants
    - Nicknames
    - Initials
    - Misspellings
    - Orthographic variations
    - Tokenization variations
    - Transliteration standard differences
    - Optional name tokens
    - Name order variations
    - Ethnicity-specific variations
    - Acronyms
    - Names in different scripts
    """
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2)

    assert result["confidence"] > 0.75, (
        f"Advanced match confidence for '{name1}' vs '{name2}' "
        f"was {result['confidence']:.3f}, expected > 0.75"
    )


def test_csv_not_empty() -> None:
    """Test that the CSV file contains test cases."""
    test_cases = load_test_cases()
    assert len(test_cases) > 0, "No test cases found in CSV file"


def test_advanced_csv_not_empty() -> None:
    """Test that the advanced CSV file contains test cases."""
    test_cases = load_advanced_test_cases()
    assert len(test_cases) > 0, "No advanced test cases found in CSV file"


def test_csv_format() -> None:
    """Test that the CSV file has the correct format."""
    with open("tests/similar_names.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        assert fieldnames == ["name1", "name2"], (
            f"Expected CSV headers to be ['name1', 'name2'], but got {fieldnames}"
        )


def test_advanced_csv_format() -> None:
    """Test that the advanced CSV file has the correct format."""
    with open("tests/advanced.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        assert fieldnames == ["name1", "name2"], (
            f"Expected advanced CSV headers to be ['name1', 'name2'], but got {fieldnames}"
        )
