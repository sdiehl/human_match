"""Data loading utilities for diminuitives and honorifics."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .core import Language
from .english import ENGLISH_HONORIFICS
from .french import FRENCH_HONORIFICS
from .german import GERMAN_HONORIFICS
from .italian import ITALIAN_HONORIFICS
from .spanish import SPANISH_HONORIFICS
from .portuguese import PORTUGUESE_HONORIFICS
from .arabic import ARABIC_HONORIFICS


@lru_cache(maxsize=1024)
def load_diminutives(language: Language, data_dir: Path) -> dict[str, list[str]]:
    """Load diminutives mapping for a language."""
    file_path = data_dir / "diminuitives" / language.value
    diminutives = {}

    if file_path.exists():
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "," in line:
                    parts = [part.strip().lower() for part in line.split(",")]
                    if len(parts) >= 2:
                        # All names in the line are equivalent - create bidirectional mapping
                        for name in parts:
                            # Each name maps to all other names in the same line
                            variants = [n for n in parts if n != name]
                            if name not in diminutives:
                                diminutives[name] = variants
                            else:
                                # Merge variants without duplicates
                                existing = set(diminutives[name])
                                existing.update(variants)
                                diminutives[name] = list(existing)

    return diminutives


@lru_cache(maxsize=1024)
def load_honorifics(language: Language, data_dir: Path) -> set[str]:
    """Load honorifics/titles for a language."""
    # Start with built-in honorifics
    honorifics_map = {
        Language.ENGLISH: ENGLISH_HONORIFICS.copy(),
        Language.FRENCH: FRENCH_HONORIFICS.copy(),
        Language.GERMAN: GERMAN_HONORIFICS.copy(),
        Language.ITALIAN: ITALIAN_HONORIFICS.copy(),
        Language.SPANISH: SPANISH_HONORIFICS.copy(),
        Language.PORTUGUESE: PORTUGUESE_HONORIFICS.copy(),
        Language.ARABIC: ARABIC_HONORIFICS.copy(),
    }

    honorifics = honorifics_map.get(language, set())

    # Load additional honorifics from file
    file_path = data_dir / "honorifics" / language.value
    if file_path.exists():
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                title = line.strip()
                if title:
                    honorifics.add(title.lower())
                    # Add variant without periods
                    honorifics.add(title.lower().replace(".", ""))

    return honorifics


def expand_diminutives(name: str, language: Language, data_dir: Path) -> list[str]:
    """Generate possible full names from diminutives."""
    diminutives = load_diminutives(language, data_dir)
    name_lower = name.lower()

    if name_lower in diminutives:
        return [name_lower] + diminutives[name_lower]

    return [name_lower]
