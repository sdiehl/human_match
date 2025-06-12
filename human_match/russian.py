"""Russian language-specific processing for name matching."""

from __future__ import annotations

import re

from nameparser import HumanName


# Russian particles that should be included with surnames
RUSSIAN_PARTICLES = {
    "де",  # de (French origin)
    "ван",  # van (Dutch origin)
    "фон",  # von (German origin)
    "ла",  # la (French origin)
    "ле",  # le (French origin)
    "дю",  # du (French origin)
    # Romanized versions
    "de",
    "van",
    "von",
    "la",
    "le",
    "du",
    "der",
    "des",
}

# Russian honorifics and titles
RUSSIAN_HONORIFICS = {
    "господин",  # Mr.
    "госпожа",  # Mrs.
    "товарищ",  # Comrade
    "доктор",  # Doctor
    "профессор",  # Professor
    "академик",  # Academician
    "генерал",  # General
    "полковник",  # Colonel
    "майор",  # Major
    "капитан",  # Captain
    "князь",  # Prince
    "княгиня",  # Princess
    "граф",  # Count
    "графиня",  # Countess
    "барон",  # Baron
    "баронесса",  # Baroness
    # Romanized versions
    "gospodin",
    "gospozha",
    "tovarisch",
    "doktor",
    "professor",
    "akademik",
    "general",
    "polkovnik",
    "mayor",
    "kapitan",
    "knyaz",
    "knyaginya",
    "graf",
    "grafinya",
    "baron",
    "baronessa",
}


def is_cyrillic_text(text: str) -> bool:
    """Check if text contains Cyrillic characters."""
    return bool(
        re.search(r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F]", text)
    )


def normalize_cyrillic_text(text: str) -> str:
    """Normalize Cyrillic text by standardizing forms."""
    if not text:
        return text

    # Remove extra spaces
    normalized = re.sub(r"\s+", " ", text.strip())

    return normalized


def romanize_russian_name(name: str) -> str:
    """Convert common Russian name patterns to romanized equivalents."""
    # Simple romanization mapping for common patterns
    romanization_map = {
        "александр": "alexander",
        "алексей": "aleksey",
        "андрей": "andrey",
        "антон": "anton",
        "артем": "artem",
        "борис": "boris",
        "владимир": "vladimir",
        "дмитрий": "dmitriy",
        "евгений": "evgeniy",
        "игорь": "igor",
        "иван": "ivan",
        "константин": "konstantin",
        "максим": "maksim",
        "михаил": "mikhail",
        "николай": "nikolay",
        "олег": "oleg",
        "павел": "pavel",
        "петр": "petr",
        "роман": "roman",
        "сергей": "sergey",
        "анна": "anna",
        "елена": "elena",
        "ирина": "irina",
        "мария": "mariya",
        "наталья": "natalya",
        "ольга": "olga",
        "светлана": "svetlana",
        "татьяна": "tatyana",
        "юлия": "yuliya",
        "екатерина": "ekaterina",
        # Add diminutive mappings
        "саша": "sasha",
        "володя": "volodya",
        "вова": "vova",
        "дима": "dima",
        "митя": "mitya",
        "маша": "masha",
        "катя": "katya",
        "наташа": "natasha",
        "серёжа": "seryozha",
        "серёга": "seryoga",
        "паша": "pasha",
        "миша": "misha",
        "лена": "lena",
        "таня": "tanya",
        "света": "sveta",
        "юля": "yulya",
    }

    name_lower = name.lower()
    for cyrillic, roman in romanization_map.items():
        if cyrillic in name_lower:
            return roman

    return name


def adjust_russian_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for Russian names with special handling for Cyrillic script."""
    # If the name contains Cyrillic script, handle it specially
    if is_cyrillic_text(name):
        words = name.split()

        # Handle Russian particles
        for i, word in enumerate(words):
            word_lower = word.lower()
            normalized_word = normalize_cyrillic_text(word_lower)

            if normalized_word in RUSSIAN_PARTICLES or word_lower in RUSSIAN_PARTICLES:
                if i > 0:  # Particle not at the beginning
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

        # Handle Russian patronymic patterns (middle names ending in -ович/-евич/-ич for males, -овна/-евна/-ична for females)
        if len(words) == 3:
            middle_name = words[1]
            if re.search(r"(ович|евич|ич|овна|евна|ична)$", middle_name, re.IGNORECASE):
                parsed.first = words[0]
                parsed.middle = words[1]  # This is the patronymic
                parsed.last = words[2]
        elif len(words) == 2:
            # Check if second word is patronymic
            second_word = words[1]
            if re.search(r"(ович|евич|ич|овна|евна|ична)$", second_word, re.IGNORECASE):
                parsed.first = words[0]
                parsed.middle = words[1]  # This is the patronymic
                parsed.last = ""
            else:
                # Standard first last pattern
                parsed.first = words[0]
                parsed.middle = ""
                parsed.last = words[1]
    else:
        # Handle romanized Russian names
        words = name.split()
        if len(words) >= 3:
            for i, word in enumerate(words):
                if word.lower() in RUSSIAN_PARTICLES and i > 0:
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

            # Handle romanized patronymic patterns
            if len(words) == 3:
                middle_name = words[1]
                if re.search(
                    r"(ovich|evich|ich|ovna|evna|ichna)$", middle_name, re.IGNORECASE
                ):
                    parsed.first = words[0]
                    parsed.middle = words[1]  # This is the patronymic
                    parsed.last = words[2]
        elif len(words) == 2:
            # Check if second word is patronymic
            second_word = words[1]
            if re.search(
                r"(ovich|evich|ich|ovna|evna|ichna)$", second_word, re.IGNORECASE
            ):
                parsed.first = words[0]
                parsed.middle = words[1]  # This is the patronymic
                parsed.last = ""
            else:
                # Standard first last pattern
                parsed.first = words[0]
                parsed.middle = ""
                parsed.last = words[1]

    return parsed


def normalize_russian_surname(surname: str) -> str:
    """Normalize Russian surname by removing particles and standardizing script."""
    if is_cyrillic_text(surname):
        # Normalize Cyrillic text
        normalized = normalize_cyrillic_text(surname.lower())
        words = normalized.split()

        # Remove particles
        filtered_words = []
        for word in words:
            if word not in RUSSIAN_PARTICLES:
                filtered_words.append(word)

        # If we removed everything, keep the original
        if not filtered_words:
            return normalized

        return " ".join(filtered_words)
    else:
        # Handle romanized Russian names
        normalized = surname.lower()
        words = normalized.split()

        # Remove particles from the beginning and keep track of the core name
        filtered_words = []
        for word in words:
            if word not in RUSSIAN_PARTICLES:
                filtered_words.append(word)

        # If we removed everything, keep the original
        if not filtered_words:
            return normalized

        return " ".join(filtered_words)


def calculate_russian_similarity(name1: str, name2: str) -> float:
    """Calculate similarity for Russian names with special handling for script variations."""
    # If both names are in Cyrillic script, use normalized comparison
    if is_cyrillic_text(name1) and is_cyrillic_text(name2):
        norm1 = normalize_cyrillic_text(name1)
        norm2 = normalize_cyrillic_text(name2)

        if norm1 == norm2:
            return 1.0

        # Try basic similarity on normalized text
        from .utils import calculate_distance

        return calculate_distance(norm1, norm2)

    # If one is Cyrillic and one is romanized, try romanization matching
    elif is_cyrillic_text(name1) and not is_cyrillic_text(name2):
        romanized1 = romanize_russian_name(name1)
        if romanized1 and romanized1 != name1:
            from .utils import calculate_distance

            # Try direct romanization match first
            direct_score = calculate_distance(romanized1, name2.lower())

            # Also try the original comparison for fallback
            fallback_score = calculate_distance(name1.lower(), name2.lower())

            return max(direct_score, fallback_score)

    elif not is_cyrillic_text(name1) and is_cyrillic_text(name2):
        romanized2 = romanize_russian_name(name2)
        if romanized2 and romanized2 != name2:
            from .utils import calculate_distance

            # Try direct romanization match first
            direct_score = calculate_distance(name1.lower(), romanized2)

            # Also try the original comparison for fallback
            fallback_score = calculate_distance(name1.lower(), name2.lower())

            return max(direct_score, fallback_score)

    # Default to standard comparison with slight boost for Russian context
    from .utils import calculate_distance

    base_score = calculate_distance(name1, name2)

    # Apply a small boost for Russian names to account for transliteration variations
    if base_score > 0.8:
        base_score = min(1.0, base_score * 1.05)

    return base_score
