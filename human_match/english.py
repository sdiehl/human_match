"""English language-specific processing for name matching."""

from __future__ import annotations

from nameparser import HumanName


# English particles that should be included with surnames
ENGLISH_PARTICLES = {"mc", "mac", "o'", "of", "the"}

# English honorifics and titles
ENGLISH_HONORIFICS = {
    "mr",
    "mr.",
    "mrs",
    "mrs.",
    "miss",
    "ms",
    "ms.",
    "dr",
    "dr.",
    "prof",
    "prof.",
    "professor",
    "sir",
    "lady",
    "lord",
    "dame",
    "rev",
    "reverend",
    "captain",
    "colonel",
    "major",
    "general",
}


def adjust_english_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for English names."""
    # Handle hyphenated names and compound surnames
    # English parsing is generally handled well by the base nameparser
    return parsed


def normalize_english_surname(surname: str) -> str:
    """Normalize English surname by handling particles appropriately."""
    # Handle apostrophes - keep for English (e.g., O'Connor)
    normalized = surname.lower()

    # For English, we generally keep particles as they're often integral
    # to the name (e.g., McDonald, O'Brien)
    return normalized
