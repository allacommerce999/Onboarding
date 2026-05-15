from __future__ import annotations

import re


TRANSLIT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "i",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def transliterate(value: str) -> str:
    result = []
    for char in value.lower():
        result.append(TRANSLIT.get(char, char))
    text = "".join(result)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def split_full_name(full_name: str) -> tuple[str, str, str]:
    parts = [part for part in full_name.strip().split() if part]
    last_name = parts[0] if parts else ""
    first_name = parts[1] if len(parts) > 1 else ""
    patronymic = parts[2] if len(parts) > 2 else ""
    return last_name, first_name, patronymic


def suggest_login(full_name: str) -> str:
    last_name, first_name, patronymic = split_full_name(full_name)
    base = transliterate(last_name)
    initials = transliterate((first_name[:1] or "") + (patronymic[:1] or ""))
    login = f"{base}{initials}"
    return login or "newemployee"


def suggest_email(full_name: str, domain: str) -> str:
    safe_domain = domain.strip() or "test12systems.ru"
    return f"{suggest_login(full_name)}@{safe_domain}"


def make_employee_slug(full_name: str, start_date: str) -> str:
    login = suggest_login(full_name)
    date_part = re.sub(r"[^0-9-]+", "", start_date) or "draft"
    return f"{date_part}_{login}"
