"""Arabic language-specific processing for name matching."""

from __future__ import annotations

import re

from nameparser import HumanName


# Arabic particles that should be included with surnames
ARABIC_PARTICLES = {
    "al",  # الـ (the)
    "el",  # variant of al
    "ibn",  # ابن (son of)
    "bin",  # بن (son of)
    "bint",  # بنت (daughter of)
    "abu",  # أبو (father of)
    "um",  # أم (mother of)
    "abd",  # عبد (servant of)
    "عبد",  # Arabic script
    "ابن",  # Arabic script
    "بن",  # Arabic script
    "بنت",  # Arabic script
    "أبو",  # Arabic script
    "أم",  # Arabic script
    "الـ",  # Arabic script (the)
}

# Arabic honorifics and titles
ARABIC_HONORIFICS = {
    "mr",
    "mrs",
    "miss",
    "ms",
    "dr",
    "prof",
    "sheikh",
    "shaikh",
    "sheikha",
    "imam",
    "hajj",
    "hajja",
    "sayyid",
    "sayyida",
    "amir",
    "amira",
    "malik",
    "malika",
    "sultan",
    "sultana",
    "أستاذ",  # Professor
    "أستاذة",  # Professor (female)
    "دكتور",  # Doctor
    "دكتورة",  # Doctor (female)
    "شيخ",  # Sheikh
    "شيخة",  # Sheikha
    "سيد",  # Sayyid
    "سيدة",  # Sayyida
    "حاج",  # Hajj
    "حاجة",  # Hajja
    "أمير",  # Amir
    "أميرة",  # Amira
    "ملك",  # Malik
    "ملكة",  # Malika
    "سلطان",  # Sultan
    "سلطانة",  # Sultana
}


def is_arabic_text(text: str) -> bool:
    """Check if text contains Arabic characters."""
    return bool(re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", text))


def normalize_arabic_text(text: str) -> str:
    """Normalize Arabic text by removing diacritics and standardizing forms."""
    if not text:
        return text

    # Remove Arabic diacritics (tashkeel)
    normalized = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", text)

    # Normalize Arabic letters to standard forms
    # Convert different forms of Alef to standard Alef
    normalized = re.sub(r"[أإآ]", "ا", normalized)

    # Convert Teh Marbuta to Heh
    normalized = re.sub(r"ة", "ه", normalized)

    # Convert different forms of Yeh to standard Yeh
    normalized = re.sub(r"[ىئ]", "ي", normalized)

    # Remove extra spaces
    normalized = re.sub(r"\s+", " ", normalized.strip())

    return normalized


def romanize_arabic_name(name: str) -> str:
    """Convert common Arabic name patterns to romanized equivalents."""
    # Simple romanization mapping for common patterns
    romanization_map = {
        "محمد": "muhammad",
        "أحمد": "ahmad",
        "علي": "ali",
        "عبدالله": "abdullah",
        "عبدالرحمن": "abdulrahman",
        "عبدالعزيز": "abdulaziz",
        "خالد": "khalid",
        "سالم": "salem",
        "عمر": "omar",
        "يوسف": "yusuf",
        "إبراهيم": "ibrahim",
        "حسن": "hassan",
        "حسين": "hussein",
        "فاطمة": "fatima",
        "عائشة": "aisha",
        "خديجة": "khadija",
        "مريم": "mariam",
        "زينب": "zainab",
        "صفية": "safiya",
    }

    name_lower = name.lower()
    for arabic, roman in romanization_map.items():
        if arabic in name_lower:
            return roman

    return name


def adjust_arabic_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for Arabic names with special handling for Arabic script."""
    # If the name contains Arabic script, handle it specially
    if is_arabic_text(name):
        words = name.split()

        # Handle Arabic particles
        for i, word in enumerate(words):
            word_lower = word.lower()
            normalized_word = normalize_arabic_text(word_lower)

            if normalized_word in ARABIC_PARTICLES or word_lower in ARABIC_PARTICLES:
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
    else:
        # Handle romanized Arabic names
        words = name.split()
        if len(words) >= 3:
            for i, word in enumerate(words):
                if word.lower() in ARABIC_PARTICLES and i > 0:
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


def normalize_arabic_surname(surname: str) -> str:
    """Normalize Arabic surname by removing particles and standardizing script."""
    if is_arabic_text(surname):
        # Normalize Arabic text
        normalized = normalize_arabic_text(surname.lower())
        words = normalized.split()

        # Remove particles
        filtered_words = []
        for word in words:
            if word not in ARABIC_PARTICLES:
                filtered_words.append(word)

        # If we removed everything, keep the original
        if not filtered_words:
            return normalized

        return " ".join(filtered_words)
    else:
        # Handle romanized Arabic names
        normalized = surname.lower()
        words = normalized.split()

        # Remove particles from the beginning and keep track of the core name
        filtered_words = []
        for word in words:
            if word not in ARABIC_PARTICLES:
                filtered_words.append(word)

        # If we removed everything, keep the original
        if not filtered_words:
            return normalized

        return " ".join(filtered_words)


def calculate_arabic_similarity(name1: str, name2: str) -> float:
    """Calculate similarity for Arabic names with special handling for script variations."""
    # If both names are in Arabic script, use normalized comparison
    if is_arabic_text(name1) and is_arabic_text(name2):
        norm1 = normalize_arabic_text(name1)
        norm2 = normalize_arabic_text(name2)

        if norm1 == norm2:
            return 1.0

        # Try basic similarity on normalized text
        from .utils import calculate_distance

        return calculate_distance(norm1, norm2)

    # If one is Arabic and one is romanized, try romanization matching
    elif is_arabic_text(name1) and not is_arabic_text(name2):
        romanized1 = romanize_arabic_name(name1)
        if romanized1 and romanized1 != name1:
            from .utils import calculate_distance

            return calculate_distance(romanized1, name2.lower())

    elif not is_arabic_text(name1) and is_arabic_text(name2):
        romanized2 = romanize_arabic_name(name2)
        if romanized2 and romanized2 != name2:
            from .utils import calculate_distance

            return calculate_distance(name1.lower(), romanized2)

    # Default to standard comparison
    from .utils import calculate_distance

    return calculate_distance(name1, name2)
