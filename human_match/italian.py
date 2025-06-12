"""Italian language-specific processing for name matching."""

from __future__ import annotations

from nameparser import HumanName


# Italian particles that should be included with surnames
ITALIAN_PARTICLES = {
    "di",
    "da",
    "del",
    "della",
    "dei",
    "delle",
    "dello",
    "degli",
    "de",
    "d'",
    "dal",
    "dalla",
    "dallo",
    "dalle",
    "san",
    "santa",
    "santo",
}

# Italian honorifics and titles
ITALIAN_HONORIFICS = {
    "signore",
    "signora",
    "signorina",
    "sig",
    "sig.",
    "dott",
    "dott.",
    "dottore",
    "dottoressa",
    "prof",
    "prof.",
    "professore",
    "professoressa",
    "ingegnere",
    "ing",
    "ing.",
    "avvocato",
    "avv",
    "avv.",
    "don",
    "donna",
    "conte",
    "contessa",
    "barone",
    "baronessa",
    "marchese",
    "marchesa",
    "duca",
    "duchessa",
}


def adjust_italian_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for Italian names."""
    # Handle Italian particles like "di", "della", "del"
    words = name.split()
    if len(words) >= 3:
        # Look for particles and combine them with the surname
        for i, word in enumerate(words):
            if (
                word.lower() in ITALIAN_PARTICLES and i > 0
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


def normalize_italian_surname(surname: str) -> str:
    """Normalize Italian surname by removing particles."""
    # Handle apostrophes - remove for Italian
    normalized = surname.lower().replace("'", "").replace("'", "")
    words = normalized.split()

    # Remove particles from the beginning and keep track of the core name
    filtered_words = []
    for word in words:
        if word not in ITALIAN_PARTICLES:
            filtered_words.append(word)

    # If we removed everything, keep the original
    if not filtered_words:
        return normalized

    return " ".join(filtered_words)
