"""Human Name Matching Engine.

A comprehensive name matching system supporting multiple languages with advanced
algorithms for segmentation, diminutives, phonetics, and distance calculation.
"""

from .core import Gender, Language, MatchResult, NameComponents
from .matcher import NameMatcher, match, match_names, match_basic

__version__ = "0.2.0"
__all__ = [
    "NameMatcher",
    "Language",
    "Gender",
    "NameComponents",
    "MatchResult",
    "match_names",
    "match",
    "match_basic",
]
