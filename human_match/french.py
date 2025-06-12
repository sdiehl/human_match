"""French language-specific processing for name matching."""

from __future__ import annotations

from nameparser import HumanName


# French particles that should be included with surnames
FRENCH_PARTICLES = {
    "de",
    "du",
    "des",
    "le",
    "la",
    "les",
    "d'",
    "di",
    "da",
    "del",
    "della",
}

# French honorifics and titles
FRENCH_HONORIFICS = {
    "m",
    "m.",
    "monsieur",
    "mme",
    "madame",
    "mlle",
    "mademoiselle",
    "dr",
    "docteur",
    "prof",
    "professeur",
    "général",
    "colonel",
    "major",
    "capitaine",
}


def adjust_french_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for French names."""
    # Handle French particles like "de", "du", "des", "le", "la"
    words = name.split()
    if len(words) >= 3:
        # Look for particles and combine them with the surname
        for i, word in enumerate(words):
            if (
                word.lower() in FRENCH_PARTICLES and i > 0
            ):  # Particle not at the beginning
                # Everything from the particle onwards is the surname
                last_part = " ".join(words[i:])
                parsed.last = last_part
                # Everything before the particle is first/middle
                if i == 1:
                    parsed.first = words[0]
                    parsed.middle = ""
                elif i == 2:
                    parsed.first = words[0]
                    parsed.middle = words[1]
                else:
                    parsed.first = " ".join(words[: i - 1])
                    parsed.middle = words[i - 1]
                break

    return parsed


def normalize_french_surname(surname: str) -> str:
    """Normalize French surname by removing particles."""
    # Handle apostrophes - remove for French
    normalized = surname.lower().replace("'", "").replace("'", "")
    words = normalized.split()

    # Remove particles from the beginning and keep track of the core name
    filtered_words = []
    for word in words:
        if word not in FRENCH_PARTICLES:
            filtered_words.append(word)

    # If we removed everything, keep the original
    if not filtered_words:
        return normalized

    return " ".join(filtered_words)
