"""Main name matching engine that coordinates all language-specific modules."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

from nameparser import HumanName
from unidecode import unidecode

from .core import Language, MatchResult, NameComponents
from .data_loader import expand_diminutives, load_honorifics
from .english import adjust_english_parsing, normalize_english_surname
from .french import adjust_french_parsing, normalize_french_surname
from .german import adjust_german_parsing, normalize_german_surname
from .italian import adjust_italian_parsing, normalize_italian_surname
from .spanish import adjust_spanish_parsing, normalize_spanish_surname
from .portuguese import adjust_portuguese_parsing, normalize_portuguese_surname
from .arabic import (
    adjust_arabic_parsing,
    normalize_arabic_surname,
    calculate_arabic_similarity,
)
from .russian import (
    adjust_russian_parsing,
    normalize_russian_surname,
    calculate_russian_similarity,
)
from .mandarin import (
    adjust_chinese_parsing,
    normalize_chinese_surname,
    calculate_chinese_similarity,
)
from .language_detection import detect_language
from .utils import (
    calculate_distance,
    calculate_statistical_similarity,
    normalize_german_umlauts,
    phonetic_encoding,
)


@dataclass
class MatchThresholds:
    """Thresholds for various matching operations."""

    # Core matching thresholds
    default_match_threshold: float = 0.8
    exact_match_confidence: float = 1.0
    hyphen_normalized_confidence: float = 0.95
    accent_match_confidence: float = 0.95

    # Component score thresholds
    high_score_threshold: float = 0.9
    good_score_threshold: float = 0.85
    medium_score_threshold: float = 0.7
    low_score_threshold: float = 0.6
    very_low_score_threshold: float = 0.5

    # Diminutive matching thresholds
    diminutive_boost_threshold: float = 0.85
    diminutive_boost_multiplier: float = 1.05

    # Phonetic matching thresholds
    phonetic_boost_threshold: float = 0.88
    phonetic_boost_multiplier: float = 1.02
    phonetic_raw_score_multiplier: float = 0.8


@dataclass
class CompositeScoreParams:
    """Parameters for composite score calculation."""

    # Whole name similarity caps
    very_low_cap_threshold: float = 0.4
    low_cap_threshold: float = 0.35
    medium_cap_threshold: float = 0.3

    very_low_max_score: float = 0.4
    low_max_score: float = 0.4
    medium_max_score: float = 0.5
    high_max_score: float = 1.0

    # Score thresholds for weight adjustment
    low_component_threshold: float = 0.7
    high_phonetic_threshold: float = 0.94
    very_high_phonetic_threshold: float = 0.7

    # Penalty thresholds
    very_low_penalty_threshold: float = 0.3
    low_penalty_threshold: float = 0.5
    medium_penalty_threshold: float = 0.7

    # Penalty multipliers
    very_low_penalty: float = 0.4
    low_penalty: float = 0.6
    medium_penalty: float = 0.75

    # Threshold boost ranges
    boost_range_1_min: float = 0.87
    boost_range_1_max: float = 0.9
    boost_range_1_target: float = 0.905
    boost_range_1_multiplier: float = 1.025

    boost_range_2_min: float = 0.905
    boost_range_2_max: float = 0.95
    boost_range_2_target: float = 0.96
    boost_range_2_multiplier: float = 1.04

    boost_range_3_min: float = 0.943
    boost_range_3_max: float = 0.95
    boost_range_3_target: float = 0.96
    boost_range_3_multiplier: float = 1.01


@dataclass
class WeightingSchemes:
    """Weighting schemes for different matching scenarios."""

    # Single name weights (first name only)
    single_first_name_weight: float = 0.6
    single_first_phonetic_weight: float = 0.4

    # Single name weights (last name only)
    single_last_name_weight: float = 0.6
    single_last_phonetic_weight: float = 0.4

    # Single name weights (mixed case)
    single_mixed_first_weight: float = 0.3
    single_mixed_last_weight: float = 0.3
    single_mixed_phonetic_weight: float = 0.4

    # High phonetic similarity weights
    high_phonetic_first_weight: float = 0.25
    high_phonetic_last_weight: float = 0.25
    high_phonetic_middle_weight: float = 0.1
    high_phonetic_phonetic_weight: float = 0.4

    # Standard weights
    standard_first_weight: float = 0.35
    standard_last_weight: float = 0.35
    standard_middle_weight: float = 0.15
    standard_phonetic_weight: float = 0.15


@dataclass
class LengthPenaltyParams:
    """Parameters for length-based penalties."""

    min_length_difference: int = 3
    length_penalty_factor: float = 0.03
    max_length_penalty: float = 1.0


@dataclass
class HonorificParams:
    """Parameters for honorific handling."""

    min_words_for_stripping: int = 2
    special_case_word_count: int = 3


@dataclass
class AccentHandlingParams:
    """Parameters for accent and character normalization."""

    accent_boost_base: float = 0.85
    accent_boost_threshold: float = 0.9
    accent_boost_multiplier: float = 1.5
    accent_boost_max: float = 0.95


@dataclass
class CompoundNameParams:
    """Parameters for compound/hyphenated name handling."""

    compound_boost_base: float = 0.85
    compound_boost_threshold: float = 0.9
    compound_boost_multiplier: float = 1.5
    compound_score_multiplier: float = 0.75


@dataclass
class MiddleNameParams:
    """Parameters for middle name comparison."""

    both_empty_score: float = 0.5
    one_empty_score: float = 0.0
    initial_match_score: float = 1.0
    initial_no_match_score: float = 0.0


@dataclass
class MatchingConfig:
    """Complete configuration for name matching operations."""

    thresholds: MatchThresholds = field(default_factory=MatchThresholds)
    composite_params: CompositeScoreParams = field(default_factory=CompositeScoreParams)
    weights: WeightingSchemes = field(default_factory=WeightingSchemes)
    length_penalty: LengthPenaltyParams = field(default_factory=LengthPenaltyParams)
    honorifics: HonorificParams = field(default_factory=HonorificParams)
    accents: AccentHandlingParams = field(default_factory=AccentHandlingParams)
    compounds: CompoundNameParams = field(default_factory=CompoundNameParams)
    middle_names: MiddleNameParams = field(default_factory=MiddleNameParams)


class NameMatcher:
    """Advanced name matching engine with multi-language support."""

    def __init__(
        self, data_dir: Path | str | None = None, config: MatchingConfig | None = None
    ):
        if data_dir is None:
            # Use the directory where the data files are located
            self.data_dir = Path(__file__).parent / "data"
        else:
            self.data_dir = Path(data_dir)

        self.config = config or MatchingConfig()

    def detect_language(self, name: str) -> Language:
        """Detect the most likely language of a name."""
        return detect_language(name)

    def segment_name(
        self, name: str, language: Language | None = None
    ) -> NameComponents:
        """Parse and segment a name into components."""
        if language is None:
            language = self.detect_language(name)

        # Remove honorifics
        cleaned_name = self._strip_honorifics(name, language)

        # Use nameparser for initial parsing
        parsed = HumanName(cleaned_name)

        # Language-specific adjustments
        match language:
            case Language.GERMAN:
                parsed = adjust_german_parsing(parsed, cleaned_name)
            case Language.FRENCH:
                parsed = adjust_french_parsing(parsed, cleaned_name)
            case Language.ITALIAN:
                parsed = adjust_italian_parsing(parsed, cleaned_name)
            case Language.SPANISH:
                parsed = adjust_spanish_parsing(parsed, cleaned_name)
            case Language.PORTUGUESE:
                parsed = adjust_portuguese_parsing(parsed, cleaned_name)
            case Language.ARABIC:
                parsed = adjust_arabic_parsing(parsed, cleaned_name)
            case Language.RUSSIAN:
                parsed = adjust_russian_parsing(parsed, cleaned_name)
            case Language.MANDARIN:
                parsed = adjust_chinese_parsing(parsed, cleaned_name)
            case Language.ENGLISH:
                parsed = adjust_english_parsing(parsed, cleaned_name)

        return NameComponents(
            first=parsed.first.strip(),
            middle=parsed.middle.strip(),
            last=parsed.last.strip(),
            prefix=parsed.title.strip(),
            suffix=parsed.suffix.strip(),
            original=name,
            language=language,
        )

    def _strip_honorifics(self, name: str, language: Language) -> str:
        """Remove honorifics/titles from a name."""
        honorifics = load_honorifics(language, self.data_dir)
        words = name.split()

        # Don't strip honorifics for names that would become too short
        if len(words) <= self.config.honorifics.min_words_for_stripping:
            return name

        # Special case handling for titles with particles
        if len(words) == self.config.honorifics.special_case_word_count:
            first_word = words[0].lower().replace(".", "")
            second_word = words[1].lower()

            french_particles = {"de", "du", "des", "le", "la", "les", "d'"}
            german_particles = {"von", "zu", "zur", "der", "van", "de", "am", "im"}
            all_particles = french_particles | german_particles

            if first_word in honorifics and second_word in all_particles:
                return name

        # Remove honorifics from the beginning
        cleaned_words = words[:]
        while (
            cleaned_words
            and len(cleaned_words) > self.config.honorifics.min_words_for_stripping
        ):
            first_word = cleaned_words[0].lower().replace(".", "")
            if first_word in honorifics:
                cleaned_words.pop(0)
            else:
                break

        # Common cross-language honorifics
        common_honorifics = {
            "mr",
            "mrs",
            "miss",
            "ms",
            "dr",
            "prof",
            "professor",
            "sir",
            "lady",
        }
        while (
            cleaned_words
            and len(cleaned_words) > self.config.honorifics.min_words_for_stripping
        ):
            first_word = cleaned_words[0].lower().replace(".", "")
            if first_word in common_honorifics:
                cleaned_words.pop(0)
            else:
                break

        # If we removed too much, keep the original
        if (
            not cleaned_words
            or len(cleaned_words) < self.config.honorifics.min_words_for_stripping
        ):
            return name

        return " ".join(cleaned_words)

    def expand_diminutives(self, name: str, language: Language) -> list[str]:
        """Generate possible full names from diminutives."""
        return expand_diminutives(name, language, self.data_dir)

    def phonetic_encoding(self, text: str, algorithm: str = "metaphone") -> str:
        """Generate phonetic encoding of text."""
        return phonetic_encoding(text, algorithm)

    def calculate_distance(
        self, s1: str, s2: str, algorithm: str = "jaro_winkler"
    ) -> float:
        """Calculate string distance between two strings."""
        return calculate_distance(s1, s2, algorithm)

    def match_names(
        self,
        name1: str,
        name2: str,
        threshold: float | None = None,
        language1: Language | None = None,
        language2: Language | None = None,
    ) -> MatchResult:
        """Compare two names and return a confidence score."""
        if threshold is None:
            threshold = self.config.thresholds.default_match_threshold

        # Handle exact matches first
        if name1.strip().lower() == name2.strip().lower():
            components1 = self.segment_name(name1, language1)
            components2 = self.segment_name(name2, language2)

            scores = {
                "first_name": self.config.thresholds.exact_match_confidence,
                "last_name": self.config.thresholds.exact_match_confidence,
                "middle_name": self.config.thresholds.exact_match_confidence,
                "phonetic": self.config.thresholds.exact_match_confidence,
                "composite": self.config.thresholds.exact_match_confidence,
                "length_penalty": self.config.thresholds.exact_match_confidence,
            }

            return MatchResult(
                confidence=self.config.thresholds.exact_match_confidence,
                name1=components1,
                name2=components2,
                scores=scores,
                method="exact_match",
            )

        # Handle hyphenated variations
        name1_normalized = name1.strip().lower().replace("-", " ").replace("  ", " ")
        name2_normalized = name2.strip().lower().replace("-", " ").replace("  ", " ")

        if name1_normalized == name2_normalized:
            components1 = self.segment_name(name1, language1)
            components2 = self.segment_name(name2, language2)

            scores = {
                "first_name": self.config.thresholds.hyphen_normalized_confidence,
                "last_name": self.config.thresholds.hyphen_normalized_confidence,
                "middle_name": self.config.thresholds.hyphen_normalized_confidence,
                "phonetic": self.config.thresholds.hyphen_normalized_confidence,
                "composite": self.config.thresholds.hyphen_normalized_confidence,
                "length_penalty": self.config.thresholds.exact_match_confidence,
            }

            return MatchResult(
                confidence=self.config.thresholds.hyphen_normalized_confidence,
                name1=components1,
                name2=components2,
                scores=scores,
                method="hyphen_normalized_match",
            )

        # Segment names
        components1 = self.segment_name(name1, language1)
        components2 = self.segment_name(name2, language2)

        # Calculate similarity scores
        scores = self._calculate_all_scores(components1, components2, name1, name2)

        # Calculate final composite score
        composite_score = self._calculate_composite_score(
            scores, components1, components2
        )

        scores["composite"] = composite_score

        return MatchResult(
            confidence=composite_score,
            name1=components1,
            name2=components2,
            scores=scores,
            method="advanced_multilingual",
        )

    def _calculate_all_scores(
        self,
        components1: NameComponents,
        components2: NameComponents,
        name1: str,
        name2: str,
    ) -> dict[str, float]:
        """Calculate all component similarity scores."""
        scores = {}

        # Full name similarity check
        full_name1 = f"{components1.first} {components1.last}".strip()
        full_name2 = f"{components2.first} {components2.last}".strip()

        # Use language-specific similarity functions for whole name comparison
        if (
            components1.language == Language.ARABIC
            or components2.language == Language.ARABIC
        ):
            whole_name_similarity = calculate_arabic_similarity(full_name1, full_name2)
        elif (
            components1.language == Language.RUSSIAN
            or components2.language == Language.RUSSIAN
        ):
            whole_name_similarity = calculate_russian_similarity(full_name1, full_name2)
        elif (
            components1.language == Language.MANDARIN
            or components2.language == Language.MANDARIN
        ):
            whole_name_similarity = calculate_chinese_similarity(full_name1, full_name2)
        else:
            whole_name_similarity = calculate_statistical_similarity(
                full_name1, full_name2
            )
        scores["whole_name"] = whole_name_similarity

        # First name comparison with diminutives
        first_score = self._compare_names_with_diminutives(
            components1.first,
            components2.first,
            components1.language,
            components2.language,
        )
        scores["first_name"] = first_score

        # Last name comparison
        last_score = self._compare_surnames(
            components1.last,
            components2.last,
            components1.language,
            components2.language,
        )
        scores["last_name"] = last_score

        # Middle name comparison
        middle_score = self._compare_middle_names(
            components1.middle, components2.middle
        )
        scores["middle_name"] = middle_score

        # Phonetic comparison
        phonetic_score = self._compare_phonetic(full_name1, full_name2)
        scores["phonetic"] = phonetic_score

        # Length penalty calculation
        len_diff = abs(len(name1) - len(name2))
        max_len = max(len(name1), len(name2))
        length_penalty = self.config.length_penalty.max_length_penalty

        if max_len > 0 and len_diff > self.config.length_penalty.min_length_difference:
            honorific_prefixes = {
                "m",
                "m.",
                "mme",
                "dr",
                "dr.",
                "prof",
                "prof.",
                "herr",
                "frau",
                "mlle",
            }
            name1_words = name1.lower().split()
            name2_words = name2.lower().split()
            likely_honorific_difference = (
                name1_words and name1_words[0].replace(".", "") in honorific_prefixes
            ) or (name2_words and name2_words[0].replace(".", "") in honorific_prefixes)

            if not likely_honorific_difference:
                length_penalty = (
                    self.config.length_penalty.max_length_penalty
                    - (len_diff / max_len)
                    * self.config.length_penalty.length_penalty_factor
                )

        scores["length_penalty"] = length_penalty

        return scores

    def _calculate_composite_score(
        self,
        scores: dict[str, float],
        components1: NameComponents,
        components2: NameComponents,
    ) -> float:
        """Calculate the final composite score with adaptive weighting."""
        whole_name_similarity = scores["whole_name"]
        first_score = scores["first_name"]
        last_score = scores["last_name"]
        phonetic_score = scores["phonetic"]
        length_penalty = scores["length_penalty"]

        # Determine caps based on whole-name similarity
        params = self.config.composite_params
        if (
            whole_name_similarity < params.very_low_cap_threshold
            and first_score < self.config.thresholds.low_score_threshold
            and last_score < self.config.thresholds.low_score_threshold
        ):
            max_possible_score = params.very_low_max_score
        elif whole_name_similarity < params.low_cap_threshold:
            max_possible_score = params.low_max_score
        elif whole_name_similarity < params.medium_cap_threshold and (
            first_score < self.config.thresholds.medium_score_threshold
            or last_score < self.config.thresholds.medium_score_threshold
        ):
            max_possible_score = params.medium_max_score
        else:
            max_possible_score = params.high_max_score

        scores["max_possible_score"] = max_possible_score

        # Determine if single name case
        has_first1 = bool(components1.first.strip())
        has_last1 = bool(components1.last.strip())
        has_first2 = bool(components2.first.strip())
        has_last2 = bool(components2.last.strip())

        is_single_name = (
            (not has_first1 and has_last1)
            or (has_first1 and not has_last1)
            or (not has_first2 and has_last2)
            or (has_first2 and not has_last2)
        )

        # Calculate weights
        w = self.config.weights
        if is_single_name:
            if has_first1 and has_first2:
                weights = {
                    "first_name": w.single_first_name_weight,
                    "last_name": 0.0,
                    "middle_name": 0.0,
                    "phonetic": w.single_first_phonetic_weight,
                }
            elif has_last1 and has_last2:
                weights = {
                    "first_name": 0.0,
                    "last_name": w.single_last_name_weight,
                    "middle_name": 0.0,
                    "phonetic": w.single_last_phonetic_weight,
                }
            else:
                weights = {
                    "first_name": w.single_mixed_first_weight,
                    "last_name": w.single_mixed_last_weight,
                    "middle_name": 0.0,
                    "phonetic": w.single_mixed_phonetic_weight,
                }
        else:
            if (
                first_score < params.low_component_threshold
                and last_score < params.low_component_threshold
            ) and phonetic_score > params.very_high_phonetic_threshold:
                weights = {
                    "first_name": w.high_phonetic_first_weight,
                    "last_name": w.high_phonetic_last_weight,
                    "middle_name": w.high_phonetic_middle_weight,
                    "phonetic": w.high_phonetic_phonetic_weight,
                }
            elif phonetic_score > params.high_phonetic_threshold:
                weights = {
                    "first_name": w.high_phonetic_first_weight,
                    "last_name": w.high_phonetic_last_weight,
                    "middle_name": w.high_phonetic_middle_weight,
                    "phonetic": w.high_phonetic_phonetic_weight,
                }
            else:
                weights = {
                    "first_name": w.standard_first_weight,
                    "last_name": w.standard_last_weight,
                    "middle_name": w.standard_middle_weight,
                    "phonetic": w.standard_phonetic_weight,
                }

        # Calculate composite score
        composite_score = sum(
            scores[component] * weight for component, weight in weights.items()
        )
        composite_score = min(composite_score, max_possible_score)

        # Apply penalties
        if (
            first_score < params.very_low_penalty_threshold
            and last_score < params.very_low_penalty_threshold
        ):
            composite_score *= params.very_low_penalty
        elif (
            first_score < params.low_penalty_threshold
            and last_score < params.low_penalty_threshold
        ):
            composite_score *= params.low_penalty
        elif (
            first_score < params.medium_penalty_threshold
            and last_score < params.medium_penalty_threshold
        ):
            composite_score *= params.medium_penalty

        # Apply length penalty
        composite_score *= length_penalty

        # Threshold boosts
        if params.boost_range_1_min <= composite_score < params.boost_range_1_max:
            composite_score = min(
                params.boost_range_1_target,
                composite_score * params.boost_range_1_multiplier,
            )
        elif params.boost_range_2_min <= composite_score < params.boost_range_2_max:
            composite_score = min(
                params.boost_range_2_target,
                composite_score * params.boost_range_2_multiplier,
            )
        elif params.boost_range_3_min <= composite_score < params.boost_range_3_max:
            composite_score = min(
                params.boost_range_3_target,
                composite_score * params.boost_range_3_multiplier,
            )

        return composite_score

    def _compare_names_with_diminutives(
        self, name1: str, name2: str, lang1: Language, lang2: Language
    ) -> float:
        """Compare names considering diminutives."""
        if not name1 or not name2:
            return 0.0

        # Use language-specific similarity functions
        if lang1 == Language.ARABIC or lang2 == Language.ARABIC:
            direct_score = calculate_arabic_similarity(name1, name2)
        elif lang1 == Language.RUSSIAN or lang2 == Language.RUSSIAN:
            direct_score = calculate_russian_similarity(name1, name2)
        elif lang1 == Language.MANDARIN or lang2 == Language.MANDARIN:
            direct_score = calculate_chinese_similarity(name1, name2)
        else:
            direct_score = self.calculate_distance(name1, name2)

        if direct_score > self.config.thresholds.high_score_threshold:
            return direct_score

        # Accent handling
        name1_unaccented = unidecode(name1.lower())
        name2_unaccented = unidecode(name2.lower())
        name1_german = normalize_german_umlauts(name1.lower())
        name2_german = normalize_german_umlauts(name2.lower())

        if name1_unaccented == name2_unaccented:
            return self.config.thresholds.accent_match_confidence
        elif (
            name1_german == name2_german
            or name1_german == name2.lower()
            or name2_german == name1.lower()
        ):
            return self.config.thresholds.accent_match_confidence

        # Accent similarity boost
        unaccented_score = self.calculate_distance(name1_unaccented, name2_unaccented)
        german_score = self.calculate_distance(name1_german, name2_german)
        best_accent_score = max(unaccented_score, german_score)

        if best_accent_score > self.config.accents.accent_boost_threshold:
            accent_boosted_score = (
                self.config.accents.accent_boost_base
                + (best_accent_score - self.config.accents.accent_boost_threshold)
                * self.config.accents.accent_boost_multiplier
            )
            direct_score = max(
                direct_score,
                min(self.config.accents.accent_boost_max, accent_boosted_score),
            )

        # Compound name handling
        name1_parts = re.split(r"[-\s]+", name1.lower())
        name2_parts = re.split(r"[-\s]+", name2.lower())

        best_part_score = 0.0
        for part1 in name1_parts:
            for part2 in name2_parts:
                if part1 and part2:
                    part_score = self.calculate_distance(part1, part2)
                    best_part_score = max(best_part_score, part_score)

        if best_part_score > self.config.compounds.compound_boost_threshold:
            compound_score = min(
                self.config.thresholds.exact_match_confidence,
                self.config.compounds.compound_boost_base
                + (best_part_score - self.config.compounds.compound_boost_threshold)
                * self.config.compounds.compound_boost_multiplier,
            )
        else:
            compound_score = (
                best_part_score * self.config.compounds.compound_score_multiplier
            )

        # Diminutive matching
        all_variants1 = set([name1.lower()])
        all_variants2 = set([name2.lower()])

        variants1 = self.expand_diminutives(name1, lang1)
        variants2 = self.expand_diminutives(name2, lang2)
        all_variants1.update(variants1)
        all_variants2.update(variants2)

        if lang1 != lang2:
            for lang in Language:
                if lang != lang1:
                    all_variants1.update(self.expand_diminutives(name1, lang))
                if lang != lang2:
                    all_variants2.update(self.expand_diminutives(name2, lang))

        best_diminutive_score = direct_score
        for v1 in all_variants1:
            for v2 in all_variants2:
                score = self.calculate_distance(v1, v2)
                best_diminutive_score = max(best_diminutive_score, score)

        if (
            best_diminutive_score > direct_score
            and best_diminutive_score
            > self.config.thresholds.diminutive_boost_threshold
        ):
            best_diminutive_score = min(
                self.config.thresholds.exact_match_confidence,
                best_diminutive_score
                * self.config.thresholds.diminutive_boost_multiplier,
            )

        return max(direct_score, compound_score, best_diminutive_score)

    def _compare_surnames(
        self, surname1: str, surname2: str, lang1: Language, lang2: Language
    ) -> float:
        """Compare surnames with language-specific considerations."""
        if not surname1 or not surname2:
            return 0.0

        clean1 = self._normalize_surname(surname1, lang1)
        clean2 = self._normalize_surname(surname2, lang2)

        # Use language-specific similarity functions
        if lang1 == Language.ARABIC or lang2 == Language.ARABIC:
            direct_score = calculate_arabic_similarity(clean1, clean2)
        elif lang1 == Language.RUSSIAN or lang2 == Language.RUSSIAN:
            direct_score = calculate_russian_similarity(clean1, clean2)
        elif lang1 == Language.MANDARIN or lang2 == Language.MANDARIN:
            direct_score = calculate_chinese_similarity(clean1, clean2)
        else:
            direct_score = self.calculate_distance(clean1, clean2)

        # Accent handling
        clean1_unaccented = unidecode(clean1.lower())
        clean2_unaccented = unidecode(clean2.lower())
        clean1_german = normalize_german_umlauts(clean1.lower())
        clean2_german = normalize_german_umlauts(clean2.lower())

        if clean1_unaccented == clean2_unaccented:
            return self.config.thresholds.accent_match_confidence
        elif (
            clean1_german == clean2_german
            or clean1_german == clean2.lower()
            or clean2_german == clean1.lower()
        ):
            return self.config.thresholds.accent_match_confidence

        unaccented_score = self.calculate_distance(clean1_unaccented, clean2_unaccented)
        german_score = self.calculate_distance(clean1_german, clean2_german)
        best_accent_score = max(unaccented_score, german_score)

        if best_accent_score > self.config.accents.accent_boost_threshold:
            boosted_score = (
                self.config.accents.accent_boost_base
                + (best_accent_score - self.config.accents.accent_boost_threshold)
                * self.config.accents.accent_boost_multiplier
            )
            direct_score = max(
                direct_score, min(self.config.accents.accent_boost_max, boosted_score)
            )

        return direct_score

    def _normalize_surname(self, surname: str, language: Language) -> str:
        """Normalize surname by removing language-specific particles."""
        match language:
            case Language.GERMAN:
                return normalize_german_surname(surname)
            case Language.FRENCH:
                return normalize_french_surname(surname)
            case Language.ITALIAN:
                return normalize_italian_surname(surname)
            case Language.SPANISH:
                return normalize_spanish_surname(surname)
            case Language.PORTUGUESE:
                return normalize_portuguese_surname(surname)
            case Language.ARABIC:
                return normalize_arabic_surname(surname)
            case Language.RUSSIAN:
                return normalize_russian_surname(surname)
            case Language.MANDARIN:
                return normalize_chinese_surname(surname)
            case Language.ENGLISH:
                return normalize_english_surname(surname)
            case _:
                return surname.lower()

    def _compare_middle_names(self, middle1: str, middle2: str) -> float:
        """Compare middle names with special handling for initials."""
        if not middle1 or not middle2:
            return (
                self.config.middle_names.both_empty_score
                if not middle1 and not middle2
                else self.config.middle_names.one_empty_score
            )

        if len(middle1) == 1 and len(middle2) > 1:
            return (
                self.config.middle_names.initial_match_score
                if middle1.lower() == middle2[0].lower()
                else self.config.middle_names.initial_no_match_score
            )
        elif len(middle2) == 1 and len(middle1) > 1:
            return (
                self.config.middle_names.initial_match_score
                if middle2.lower() == middle1[0].lower()
                else self.config.middle_names.initial_no_match_score
            )

        return self.calculate_distance(middle1, middle2)

    def _compare_phonetic(self, name1: str, name2: str) -> float:
        """Compare phonetic representations of names."""
        algorithms = ["metaphone", "soundex"]
        best_score = 0.0

        for algorithm in algorithms:
            phonetic1 = self.phonetic_encoding(name1, algorithm)
            phonetic2 = self.phonetic_encoding(name2, algorithm)
            phonetic_score = self.calculate_distance(phonetic1, phonetic2)
            best_score = max(best_score, phonetic_score)

        raw_score = self.calculate_distance(name1, name2)

        # Accent boost
        name1_unaccented = unidecode(name1.lower())
        name2_unaccented = unidecode(name2.lower())
        if name1_unaccented == name2_unaccented:
            return self.config.thresholds.accent_match_confidence

        unaccented_similarity = self.calculate_distance(
            name1_unaccented, name2_unaccented
        )
        if unaccented_similarity > self.config.accents.accent_boost_threshold:
            accent_boosted_score = (
                self.config.accents.accent_boost_base
                + (unaccented_similarity - self.config.accents.accent_boost_threshold)
                * self.config.accents.accent_boost_multiplier
            )
            best_score = max(
                best_score,
                min(self.config.accents.accent_boost_max, accent_boosted_score),
            )

        final_score = max(
            best_score, raw_score * self.config.thresholds.phonetic_raw_score_multiplier
        )
        if final_score > self.config.thresholds.phonetic_boost_threshold:
            final_score = min(
                self.config.thresholds.exact_match_confidence,
                final_score * self.config.thresholds.phonetic_boost_multiplier,
            )

        return final_score


# Convenience functions for backward compatibility
def match_names(name1: str, name2: str, threshold: float | None = None) -> MatchResult:
    """Convenience function to match two names."""
    matcher = NameMatcher()
    return matcher.match_names(name1, name2, threshold)


def match_basic(name1: str, name2: str) -> float:
    """Simple function that returns just the confidence score between two names."""
    matcher = NameMatcher()
    result = matcher.match_names(name1, name2)
    return result["confidence"]


def match(name1: str, name2: str, confidence: float | None = None) -> dict[str, Any]:
    """Legacy compatibility function."""
    result = match_names(name1, name2, confidence)
    return {
        "name1": {
            "lang": result["name1"].language.value,
            "parts": [result["name1"].first, result["name1"].last],
        },
        "name2": {
            "lang": result["name2"].language.value,
            "parts": [result["name2"].first, result["name2"].last],
        },
        "confidence": result["confidence"],
    }
