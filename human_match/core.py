"""Core data structures and enums for the human name matching engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TypedDict


class Language(Enum):
    """Supported languages for name matching."""

    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    SPANISH = "es"
    PORTUGUESE = "pt"
    ARABIC = "ar"
    RUSSIAN = "ru"
    MANDARIN = "zh"


class Gender(Enum):
    """Gender classification results."""

    MALE = auto()
    FEMALE = auto()
    NEUTRAL = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class NameComponents:
    """Structured representation of name components."""

    first: str = ""
    middle: str = ""
    last: str = ""
    prefix: str = ""
    suffix: str = ""
    original: str = ""
    language: Language = Language.ENGLISH


class MatchResult(TypedDict):
    """Result of name matching operation."""

    confidence: float
    name1: NameComponents
    name2: NameComponents
    scores: dict[str, float]
    method: str
