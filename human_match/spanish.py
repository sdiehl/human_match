"""Spanish language-specific processing for name matching."""

from __future__ import annotations

from nameparser import HumanName


# Spanish particles that should be included with surnames
SPANISH_PARTICLES = {
    "de",
    "del",
    "de la",
    "de las",
    "de los",
    "y",
    "e",
    "san",
    "santa",
    "santo",
    "da",
    "das",
    "dos",
    "do",
}

# Spanish honorifics and titles
SPANISH_HONORIFICS = {
    "señor",
    "señora",
    "señorita",
    "sr",
    "sr.",
    "sra",
    "sra.",
    "srta",
    "srta.",
    "don",
    "doña",
    "doctor",
    "doctora",
    "dr",
    "dr.",
    "dra",
    "dra.",
    "profesor",
    "profesora",
    "prof",
    "prof.",
    "ingeniero",
    "ingeniera",
    "ing",
    "ing.",
    "licenciado",
    "licenciada",
    "lic",
    "lic.",
    "arquitecto",
    "arquitecta",
    "arq",
    "arq.",
    "conde",
    "condesa",
    "duque",
    "duquesa",
    "marqués",
    "marquesa",
    "barón",
    "baronesa",
}


def adjust_spanish_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for Spanish names."""
    # Handle Spanish particles like "de", "del", "de la"
    words = name.split()
    if len(words) >= 3:
        # Look for particles and combine them with the surname
        for i, word in enumerate(words):
            if (
                word.lower() in SPANISH_PARTICLES and i > 0
            ):  # Particle not at the beginning
                # Check for compound particles like "de la"
                if i < len(words) - 1:
                    two_word_particle = f"{word.lower()} {words[i + 1].lower()}"
                    if two_word_particle in SPANISH_PARTICLES:
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

                # Single word particle
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


def normalize_spanish_surname(surname: str) -> str:
    """Normalize Spanish surname by removing particles."""
    # Handle apostrophes - remove for Spanish
    normalized = surname.lower().replace("'", "").replace("'", "")
    words = normalized.split()

    # Remove particles from the beginning and keep track of the core name
    filtered_words = []
    i = 0
    while i < len(words):
        word = words[i]
        # Check for compound particles
        if i < len(words) - 1:
            two_word_particle = f"{word} {words[i + 1]}"
            if two_word_particle in SPANISH_PARTICLES:
                i += 2  # Skip both words
                continue

        if word not in SPANISH_PARTICLES:
            filtered_words.append(word)
        i += 1

    # If we removed everything, keep the original
    if not filtered_words:
        return normalized

    return " ".join(filtered_words)
