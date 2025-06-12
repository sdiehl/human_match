"""Mandarin/Chinese language-specific processing for name matching."""

from __future__ import annotations

import re

from nameparser import HumanName

try:
    import pypinyin

    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False


# Common Chinese surnames in simplified and traditional characters
# Top 100 most common Chinese surnames
CHINESE_SURNAMES = {
    # Simplified characters
    "王",
    "李",
    "张",
    "刘",
    "陈",
    "杨",
    "黄",
    "赵",
    "周",
    "吴",
    "徐",
    "孙",
    "朱",
    "马",
    "胡",
    "郭",
    "林",
    "何",
    "高",
    "梁",
    "郑",
    "罗",
    "宋",
    "谢",
    "唐",
    "韩",
    "曹",
    "许",
    "邓",
    "萧",
    "冯",
    "曾",
    "程",
    "蔡",
    "彭",
    "潘",
    "袁",
    "于",
    "董",
    "余",
    "苏",
    "叶",
    "吕",
    "魏",
    "蒋",
    "田",
    "杜",
    "丁",
    "沈",
    "姜",
    "范",
    "江",
    "傅",
    "钟",
    "卢",
    "汪",
    "戴",
    "崔",
    "任",
    "陆",
    "廖",
    "姚",
    "方",
    "金",
    "邱",
    "夏",
    "谭",
    "韦",
    "贾",
    "邹",
    "石",
    "熊",
    "孟",
    "秦",
    "阎",
    "薛",
    "侯",
    "雷",
    "白",
    "龙",
    "段",
    "郝",
    "孔",
    "邵",
    "史",
    "毛",
    "常",
    "万",
    "顾",
    "赖",
    "武",
    "康",
    "贺",
    "严",
    "尹",
    "钱",
    "施",
    "牛",
    "洪",
    "龚",
    # Traditional characters (some different from simplified)
    "張",
    "劉",
    "陳",
    "楊",
    "黃",
    "趙",
    "週",
    "吳",
    "徐",
    "孫",
    "朱",
    "馬",
    "胡",
    "郭",
    "林",
    "何",
    "高",
    "梁",
    "鄭",
    "羅",
    "宋",
    "謝",
    "唐",
    "韓",
    "曹",
    "許",
    "鄧",
    "蕭",
    "馮",
    "曾",
    "程",
    "蔡",
    "彭",
    "潘",
    "袁",
    "於",
    "董",
    "餘",
    "蘇",
    "葉",
    "呂",
    "魏",
    "蔣",
    "田",
    "杜",
    "丁",
    "沈",
    "姜",
    "範",
    "江",
    "傅",
    "鍾",
    "盧",
    "汪",
    "戴",
    "崔",
    "任",
    "陸",
    "廖",
    "姚",
    "方",
    "金",
    "邱",
    "夏",
    "譚",
    "韋",
    "賈",
    "鄒",
    "石",
    "熊",
    "孟",
    "秦",
    "閻",
    "薛",
    "侯",
    "雷",
    "白",
    "龍",
    "段",
    "郝",
    "孔",
    "邵",
    "史",
    "毛",
    "常",
    "萬",
    "顧",
    "賴",
    "武",
    "康",
    "賀",
    "嚴",
    "尹",
    "錢",
    "施",
    "牛",
    "洪",
    "龔",
}

# Romanized versions of common Chinese surnames
ROMANIZED_SURNAMES = {
    "wang",
    "li",
    "zhang",
    "liu",
    "chen",
    "yang",
    "huang",
    "zhao",
    "zhou",
    "wu",
    "xu",
    "sun",
    "zhu",
    "ma",
    "hu",
    "guo",
    "lin",
    "he",
    "gao",
    "liang",
    "zheng",
    "luo",
    "song",
    "xie",
    "tang",
    "han",
    "cao",
    "xu",
    "deng",
    "xiao",
    "feng",
    "zeng",
    "cheng",
    "cai",
    "peng",
    "pan",
    "yuan",
    "yu",
    "dong",
    "yu",
    "su",
    "ye",
    "lv",
    "wei",
    "jiang",
    "tian",
    "du",
    "ding",
    "shen",
    "jiang",
    "fan",
    "jiang",
    "fu",
    "zhong",
    "lu",
    "wang",
    "dai",
    "cui",
    "ren",
    "lu",
    "liao",
    "yao",
    "fang",
    "jin",
    "qiu",
    "xia",
    "tan",
    "wei",
    "jia",
    "zou",
    "shi",
    "xiong",
    "meng",
    "qin",
    "yan",
    "xue",
    "hou",
    "lei",
    "bai",
    "long",
    "duan",
    "hao",
    "kong",
    "shao",
    "shi",
    "mao",
    "chang",
    "wan",
    "gu",
    "lai",
    "wu",
    "kang",
    "he",
    "yan",
    "yin",
    "qian",
    "shi",
    "niu",
    "hong",
    "gong",
    # Alternative romanizations
    "wong",
    "lee",
    "chang",
    "lau",
    "chan",
    "yeung",
    "wong",
    "chiu",
    "chow",
    "ng",
    "tsui",
    "soon",
    "chu",
    "mah",
    "woo",
    "kwok",
    "lam",
    "ho",
    "ko",
    "leung",
    "cheng",
    "law",
    "sung",
    "tse",
    "tong",
    "hon",
    "tso",
    "hui",
    "tang",
    "siu",
    "fung",
    "tsang",
    "ching",
    "choy",
    "pang",
    "poon",
    "yuen",
    "yue",
    "tung",
    "yue",
    "so",
    "yip",
    "lui",
    "wai",
    "cheung",
    "tin",
    "to",
    "ting",
    "sum",
    "keung",
    "fan",
    "kong",
    "foo",
    "chung",
    "lou",
    "wong",
    "toy",
    "chui",
    "yam",
    "luk",
    "liu",
    "yiu",
    "fong",
    "kam",
    "yau",
    "har",
    "tam",
    "wai",
    "kar",
    "chau",
    "sek",
    "hung",
    "mang",
    "chun",
    "yim",
    "sit",
    "hau",
    "lui",
    "pak",
    "lung",
    "tuen",
    "ho",
    "hung",
    "siu",
    "see",
    "mou",
    "sheung",
    "man",
    "koo",
    "loi",
    "mo",
    "hong",
    "hor",
    "yim",
    "wan",
    "chin",
    "see",
    "ngau",
    "hung",
    "kung",
}

# Common Chinese given names (simplified characters)
CHINESE_GIVEN_NAMES = {
    # Male names
    "伟",
    "强",
    "明",
    "华",
    "建",
    "国",
    "军",
    "峰",
    "磊",
    "勇",
    "涛",
    "超",
    "斌",
    "辉",
    "刚",
    "鹏",
    "飞",
    "凯",
    "杰",
    "亮",
    "龙",
    "志",
    "鑫",
    "海",
    "东",
    "南",
    "阳",
    "春",
    "浩",
    "天",
    "文",
    "武",
    "康",
    "健",
    "宏",
    "伟",
    "俊",
    "豪",
    "凌",
    "博",
    # Female names
    "丽",
    "红",
    "霞",
    "燕",
    "娟",
    "芳",
    "梅",
    "玲",
    "静",
    "敏",
    "艳",
    "萍",
    "莉",
    "兰",
    "英",
    "慧",
    "雪",
    "琳",
    "颖",
    "洁",
    "秀",
    "美",
    "花",
    "月",
    "宁",
    "雨",
    "婷",
    "晶",
    "欣",
    "倩",
    "娜",
    "瑶",
    "蕾",
    "薇",
    "珍",
    "琴",
    "云",
    "凤",
    "露",
    "佳",
}

# Honorifics and titles in Chinese
CHINESE_HONORIFICS = {
    "先生",
    "女士",
    "小姐",
    "太太",
    "夫人",
    "老师",
    "教授",
    "博士",
    "医生",
    "护士",
    "工程师",
    "律师",
    "经理",
    "主任",
    "董事",
    "总裁",
    "mister",
    "mr",
    "mrs",
    "miss",
    "ms",
    "dr",
    "prof",
    "professor",
}


def is_chinese_character(char: str) -> bool:
    """Check if a character is a Chinese character."""
    return bool(re.match(r"[\u4e00-\u9fff\u3400-\u4dbf]", char))


def is_chinese_text(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return any(is_chinese_character(char) for char in text)


def is_traditional_chinese(text: str) -> bool:
    """Check if text contains traditional Chinese characters."""
    # Traditional Chinese specific character ranges
    traditional_chars = re.search(r"[\u4e00-\u9fff]", text)
    if not traditional_chars:
        return False

    # Some common traditional characters not found in simplified
    traditional_indicators = {
        "龍",
        "鳳",
        "馬",
        "鳥",
        "魚",
        "車",
        "門",
        "長",
        "風",
        "雲",
        "電",
        "話",
        "學",
        "機",
        "會",
        "時",
        "間",
        "國",
        "語",
        "說",
        "個",
        "們",
        "這",
        "裡",
        "東",
        "來",
        "對",
        "開",
        "關",
        "發",
        "經",
        "過",
        "現",
        "業",
        "產",
        "動",
        "實",
        "點",
        "題",
        "體",
    }

    return any(char in traditional_indicators for char in text)


def convert_to_pinyin(text: str) -> str:
    """Convert Chinese text to pinyin."""
    if not HAS_PYPINYIN:
        return text

    if not is_chinese_text(text):
        return text

    # Convert to pinyin without tone marks
    pinyin_list = pypinyin.lazy_pinyin(text, style=pypinyin.Style.NORMAL)
    return "".join(pinyin_list)


def extract_chinese_surnames(text: str) -> list[str]:
    """Extract potential Chinese surnames from text."""
    surnames = []

    # Check for Chinese character surnames
    for char in text:
        if char in CHINESE_SURNAMES:
            surnames.append(char)

    # Check for romanized surnames
    words = text.lower().split()
    for word in words:
        if word in ROMANIZED_SURNAMES:
            surnames.append(word)

    return surnames


def adjust_chinese_parsing(parsed: HumanName, name: str) -> HumanName:
    """Adjust parsing for Chinese names."""
    original_parts = name.split()

    # If the name contains Chinese characters, handle it differently
    if is_chinese_text(name):
        # Chinese names typically have 2-3 characters total
        # Family name (1-2 chars) + given name (1-2 chars)
        chinese_chars = [char for char in name if is_chinese_character(char)]

        if len(chinese_chars) == 2:
            # Likely: [surname][given_name]
            parsed.last = chinese_chars[0]
            parsed.first = chinese_chars[1]
            parsed.middle = ""
        elif len(chinese_chars) == 3:
            # Could be: [surname][given_name1][given_name2] OR [surname1][surname2][given_name]
            if chinese_chars[0] in CHINESE_SURNAMES:
                # Single character surname
                parsed.last = chinese_chars[0]
                parsed.first = "".join(chinese_chars[1:])
                parsed.middle = ""
            else:
                # Assume compound surname (less common but exists)
                parsed.last = "".join(chinese_chars[:2])
                parsed.first = chinese_chars[2]
                parsed.middle = ""
        elif len(chinese_chars) == 4:
            # Likely compound surname + compound given name
            parsed.last = "".join(chinese_chars[:2])
            parsed.first = "".join(chinese_chars[2:])
            parsed.middle = ""
        elif len(chinese_chars) >= 5:
            # Very long name, take first 2 as surname, rest as given name
            parsed.last = "".join(chinese_chars[:2])
            parsed.first = "".join(chinese_chars[2:])
            parsed.middle = ""
    else:
        # Handle romanized Chinese names
        # Most romanized Chinese names follow Western order: [Given] [Family]
        # But sometimes they follow Chinese order: [Family] [Given]

        words = [
            word for word in original_parts if word.lower() not in CHINESE_HONORIFICS
        ]

        if len(words) == 2:
            # Check if first word is a known Chinese surname
            if words[0].lower() in ROMANIZED_SURNAMES:
                # Chinese order: [Family] [Given]
                parsed.last = words[0]
                parsed.first = words[1]
                parsed.middle = ""
            elif words[1].lower() in ROMANIZED_SURNAMES:
                # Western order: [Given] [Family]
                parsed.first = words[0]
                parsed.last = words[1]
                parsed.middle = ""
            else:
                # Default to Western order
                parsed.first = words[0]
                parsed.last = words[1]
                parsed.middle = ""
        elif len(words) == 3:
            # Could be [Given] [Middle] [Family] or [Family] [Given1] [Given2]
            if words[0].lower() in ROMANIZED_SURNAMES:
                # Chinese order with compound given name
                parsed.last = words[0]
                parsed.first = " ".join(words[1:])
                parsed.middle = ""
            else:
                # Western order with middle name
                parsed.first = words[0]
                parsed.middle = words[1]
                parsed.last = words[2]

    return parsed


def normalize_chinese_surname(surname: str) -> str:
    """Normalize Chinese surname by handling variants and romanizations."""
    if not surname:
        return ""

    # Convert to lowercase for romanized names
    normalized = surname.lower()

    # Handle common romanization variants
    romanization_variants = {
        "wong": "wang",
        "lee": "li",
        "chang": "zhang",
        "lau": "liu",
        "chan": "chen",
        "yeung": "yang",
        "chiu": "zhao",
        "chow": "zhou",
        "ng": "wu",
        "tsui": "xu",
        "soon": "sun",
        "chu": "zhu",
        "mah": "ma",
        "woo": "hu",
        "kwok": "guo",
        "lam": "lin",
        "ho": "he",
        "ko": "gao",
        "leung": "liang",
        "cheng": "zheng",
        "law": "luo",
        "sung": "song",
        "tse": "xie",
        "tong": "tang",
        "hon": "han",
        "tso": "cao",
        "hui": "xu",
        "tang": "deng",
        "siu": "xiao",
    }

    return romanization_variants.get(normalized, normalized)


def calculate_chinese_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between Chinese names with special handling."""
    from .utils import calculate_distance

    # If both are Chinese characters, use character-based comparison
    if is_chinese_text(name1) and is_chinese_text(name2):
        # Direct character comparison
        if name1 == name2:
            return 1.0

        # Character-by-character similarity
        chars1 = [char for char in name1 if is_chinese_character(char)]
        chars2 = [char for char in name2 if is_chinese_character(char)]

        if not chars1 or not chars2:
            return 0.0

        # Calculate Jaccard similarity for character sets
        set1 = set(chars1)
        set2 = set(chars2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        jaccard_score = intersection / union

        # Also consider sequence similarity
        sequence_score = calculate_distance("".join(chars1), "".join(chars2))

        # Combine both scores
        return max(jaccard_score * 0.7 + sequence_score * 0.3, sequence_score)

    # If one is Chinese and one is romanized, convert to pinyin
    elif is_chinese_text(name1) and not is_chinese_text(name2):
        pinyin1 = convert_to_pinyin(name1)
        return calculate_distance(pinyin1, name2.lower())

    elif not is_chinese_text(name1) and is_chinese_text(name2):
        pinyin2 = convert_to_pinyin(name2)
        return calculate_distance(name1.lower(), pinyin2)

    # Both are romanized, use standard comparison with normalization
    else:
        norm1 = normalize_chinese_surname(name1)
        norm2 = normalize_chinese_surname(name2)
        return calculate_distance(norm1, norm2)


def get_chinese_name_score(name: str) -> float:
    """Calculate how likely a name is to be Chinese."""
    if not name:
        return 0.0

    score = 0.0
    words = name.split()

    # Check for Chinese characters
    chinese_char_count = sum(1 for char in name if is_chinese_character(char))
    if chinese_char_count > 0:
        score += min(chinese_char_count / len(name), 1.0) * 0.8

    # Check for known Chinese surnames
    for word in words:
        if word in CHINESE_SURNAMES:
            score += 0.4
        elif word.lower() in ROMANIZED_SURNAMES:
            score += 0.3

    # Check for common Chinese given name patterns
    for word in words:
        for char in word:
            if char in CHINESE_GIVEN_NAMES:
                score += 0.1

    # Length patterns typical of Chinese names
    if is_chinese_text(name):
        char_count = len([c for c in name if is_chinese_character(c)])
        if 2 <= char_count <= 4:
            score += 0.2
    else:
        # Romanized names often have 2-3 syllables
        if 2 <= len(words) <= 3:
            score += 0.1

    return min(score, 1.0)
