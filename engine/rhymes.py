"""Движок для поиска рифм."""
import json
import os
import re
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RHYMES_FILE = os.path.join(DATA_DIR, "rhymes_dict.json")


def _load_rhymes() -> dict:
    """Загрузка словаря рифм из JSON файла."""
    if not os.path.exists(RHYMES_FILE):
        return {}
    try:
        with open(RHYMES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return {}


def get_rhymes(word: str, max_results: int = 10) -> list[str]:
    """Поиск рифм к слову.

    Args:
        word: Слово для поиска рифм.
        max_results: Максимальное количество результатов.

    Returns:
        Список рифм или пустой список.
    """
    word = word.lower().strip()
    rhymes = _load_rhymes()
    return rhymes.get(word, [])[:max_results]


def get_rhymes_by_ending(
    ending: str, min_length: int = 3, max_results: int = 15
) -> list[str]:
    """Поиск слов по окончанию.

    Args:
        ending: Окончание для поиска (например, '-ция').
        min_length: Минимальная длина слова без окончания.
        max_results: Максимальное количество результатов.

    Returns:
        Список слов с указанным окончанием.
    """
    ending = ending.lower().strip()
    rhymes = _load_rhymes()
    results = []

    for word, rhyming_words in rhymes.items():
        if word.endswith(ending) and len(word) - len(ending) >= min_length:
            results.append(word)
        for rhyme in rhyming_words:
            if rhyme.endswith(ending) and len(rhyme) - len(ending) >= min_length:
                results.append(rhyme)

    return list(set(results))[:max_results]


def find_ending_rhymes(word: str, min_suffix_length: int = 2) -> list[str]:
    """Поиск слов, рифмующихся по окончанию с указанным словом.

    Args:
        word: Исходное слово.
        min_suffix_length: Минимальная длина рифмующейся части.

    Returns:
        Список слов с похожим окончанием.
    """
    word = word.lower().strip()
    rhymes = _load_rhymes()
    results = []

    suffix_len = max(min_suffix_length, len(word) // 2)
    suffix = word[-suffix_len:]

    for w in rhymes.keys():
        if w != word and w.endswith(suffix):
            results.append(w)

    return list(set(results))[:15]


def get_rhyme_scheme_options() -> list[str]:
    """Возвращает список вариантов рифмовки.

    Returns:
        Список вариантов.
    """
    return [
        "ААББ — перекрёстная с параллельной",
        "АБАБ — перекрёстная",
        "АABB — парная",
        "АААА — сплошная",
        "ABAB — перекрёстная (как АБАБ)",
        "ABC — нет рифмы (свободный стих)",
    ]


def get_common_rhymes() -> list[str]:
    """Возвращает список наиболее популярных слов для поиска рифм.

    Returns:
        Список популярных слов.
    """
    rhymes = _load_rhymes()
    return list(rhymes.keys())[:20]
