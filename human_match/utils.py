"""Utility functions for name matching operations."""

from __future__ import annotations

import re
from functools import lru_cache

import jellyfish
from phonetics import dmetaphone, soundex
from unidecode import unidecode


@lru_cache(maxsize=1024)
def phonetic_encoding(text: str, algorithm: str = "metaphone") -> str:
    """Generate phonetic encoding of text."""
    # Normalize unicode characters and clean the text
    normalized = unidecode(text.lower().strip())
    # Keep only alphabetic characters for phonetic algorithms
    clean_text = re.sub(r"[^a-z]", "", normalized)

    if not clean_text:
        return normalized if normalized else text.lower()

    try:
        match algorithm:
            case "metaphone":
                result = dmetaphone(clean_text)[0]
                return result if result else clean_text
            case "soundex":
                result = soundex(clean_text)
                return result if result else clean_text
            case _:
                return clean_text
    except (IndexError, ValueError, TypeError):
        # Fallback to the clean text if phonetic algorithm fails
        return clean_text if clean_text else normalized if normalized else text.lower()


def calculate_distance(s1: str, s2: str, algorithm: str = "jaro_winkler") -> float:
    """Calculate string distance between two strings."""
    # Normalize hyphenated names for comparison
    s1_norm = s1.lower().strip().replace("-", " ").replace("  ", " ")
    s2_norm = s2.lower().strip().replace("-", " ").replace("  ", " ")

    if s1_norm == s2_norm:
        return 1.0

    match algorithm:
        case "jaro_winkler":
            return float(jellyfish.jaro_winkler_similarity(s1_norm, s2_norm))
        case "jaro":
            return float(jellyfish.jaro_similarity(s1_norm, s2_norm))
        case "levenshtein":
            max_len = max(len(s1_norm), len(s2_norm))
            if max_len == 0:
                return 1.0
            dist = jellyfish.levenshtein_distance(s1_norm, s2_norm)
            return 1.0 - (float(dist) / max_len)
        case _:
            return float(jellyfish.jaro_winkler_similarity(s1_norm, s2_norm))


def calculate_statistical_similarity(name1: str, name2: str) -> float:
    """
    Calculate statistical similarity using multiple factors:
    - Character overlap ratio
    - Positional character similarity
    - Length ratio penalty
    - N-gram overlap
    - Edit distance normalized by length
    """
    if not name1 or not name2:
        return 0.0

    # Normalize inputs
    n1 = name1.lower().strip()
    n2 = name2.lower().strip()

    if n1 == n2:
        return 1.0

    len1, len2 = len(n1), len(n2)
    max_len = max(len1, len2)
    min_len = min(len1, len2)

    if max_len == 0:
        return 1.0

    # Factor 1: Length ratio penalty (longer strings require more similarity)
    length_ratio = min_len / max_len
    length_penalty = 0.5 + (length_ratio * 0.5)  # Scale from 0.5 to 1.0

    # Factor 2: Character overlap ratio
    chars1 = set(n1)
    chars2 = set(n2)
    char_overlap = len(chars1 & chars2) / len(chars1 | chars2) if chars1 | chars2 else 0

    # Factor 3: Positional character similarity (weighted by position)
    positional_score = 0.0
    for i in range(min_len):
        if n1[i] == n2[i]:
            # Weight early positions more heavily
            weight = 1.0 - (i / max(max_len, 10))  # Diminishing weight
            positional_score += weight
    positional_score = positional_score / min_len if min_len > 0 else 0

    # Factor 4: Bigram overlap
    bigrams1 = set(n1[i : i + 2] for i in range(len(n1) - 1))
    bigrams2 = set(n2[i : i + 2] for i in range(len(n2) - 1))
    bigram_overlap = (
        len(bigrams1 & bigrams2) / len(bigrams1 | bigrams2)
        if bigrams1 | bigrams2
        else 0
    )

    # Factor 5: Edit distance normalized by max length
    try:
        edit_dist = jellyfish.levenshtein_distance(n1, n2)
        edit_similarity = 1.0 - (edit_dist / max_len)
    except (ValueError, TypeError):
        edit_similarity = 0.0

    # Factor 6: Jaro-Winkler as one component (not dominant)
    try:
        jw_similarity = jellyfish.jaro_winkler_similarity(n1, n2)
    except (ValueError, TypeError):
        jw_similarity = 0.0

    # Weighted combination of factors
    weights = {
        "length_penalty": 0.15,
        "char_overlap": 0.20,
        "positional": 0.25,
        "bigram": 0.15,
        "edit": 0.15,
        "jaro_winkler": 0.10,
    }

    combined_score = (
        weights["length_penalty"] * length_penalty
        + weights["char_overlap"] * char_overlap
        + weights["positional"] * positional_score
        + weights["bigram"] * bigram_overlap
        + weights["edit"] * edit_similarity
        + weights["jaro_winkler"] * jw_similarity
    )

    # Additional penalty for very short strings with low overlap
    if max_len < 6 and char_overlap < 0.5:
        combined_score *= 0.7

    # Additional penalty for very different lengths
    if length_ratio < 0.6:
        combined_score *= 0.5 + length_ratio * 0.5

    return min(1.0, max(0.0, combined_score))


def normalize_german_umlauts(text: str) -> str:
    """Normalize German umlauts to their expanded forms (ü->ue, ä->ae, ö->oe)."""
    replacements = {"ü": "ue", "ä": "ae", "ö": "oe", "ß": "ss"}

    result = text
    for umlaut, replacement in replacements.items():
        result = result.replace(umlaut, replacement)

    return result
