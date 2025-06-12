"""Portuguese language-specific processing for name matching."""

from __future__ import annotations

from nameparser import HumanName


# Portuguese particles that should be included with surnames
PORTUGUESE_PARTICLES = {
    "da",
    "das",
    "de",
    "del",
    "do",
    "dos",
    "e",
    "y",
    "san",
    "santa",
    "santo",
    "são",
}

# Portuguese honorifics and titles
PORTUGUESE_HONORIFICS = {
    "sr",
    "sra",
    "srta",
    "dr",
    "dra",
    "prof",
    "professora",
    "professor",
    "eng",
    "engenheiro",
    "engenheira",
    "arq",
    "arquiteto",
    "arquiteta",
    "adv",
    "advogado",
    "advogada",
    "dom",
    "dona",
    "frei",
    "padre",
    "irmã",
    "irmão",
    "general",
    "coronel",
    "major",
    "capitão",
    "tenente",
    "sargento",
    "cabo",
    "soldado",
}


def adjust_portuguese_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for Portuguese names."""
    # Handle Portuguese particles like "da", "dos", "de"
    words = name.split()
    if len(words) >= 3:
        # Look for particles and combine them with the surname
        for i, word in enumerate(words):
            if (
                word.lower() in PORTUGUESE_PARTICLES and i > 0
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


def normalize_portuguese_surname(surname: str) -> str:
    """Normalize Portuguese surname by removing particles."""
    # Handle apostrophes - keep for Portuguese (used in some names)
    normalized = surname.lower()
    words = normalized.split()

    # Remove particles from the beginning and keep track of the core name
    filtered_words = []
    for word in words:
        if word not in PORTUGUESE_PARTICLES:
            filtered_words.append(word)

    # If we removed everything, keep the original
    if not filtered_words:
        return normalized

    return " ".join(filtered_words)
