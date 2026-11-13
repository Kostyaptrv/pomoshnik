"""Подсчёт слогов и анализ ритма для русского языка."""


VOWELS = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"


def count_syllables(word: str) -> int:
    """Подсчитывает количество слогов в слове.
    
    Каждый гласный звук = один слог.
    
    Args:
        word: Слово для подсчёта слогов.
        
    Returns:
        Количество слогов.
    """
    word = word.lower().strip()
    if not word:
        return 0
    
    count = 0
    prev_was_vowel = False
    
    for char in word:
        is_vowel = char in VOWELS
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel

    return max(1, count)


def count_line_syllables(line: str) -> int:
    """Подсчитывает общее количество слогов в строке.
    
    Args:
        line: Строка текста.
        
    Returns:
        Общее количество слогов.
    """
    words = line.strip().split()
    total = 0
    for word in words:
        # Убираем пунктуацию
        clean_word = "".join(c for c in word if c.isalpha() or c in VOWELS)
        if clean_word:
            total += count_syllables(clean_word)
    return total


def get_word_syllables(word: str) -> list:
    """Возвращает список кортежей (слово, количество_слогоов) для каждой части слова.
    
    Args:
        word: Слово для анализа.
        
    Returns:
        Список кортежей (слово, слоги).
    """
    word = word.lower().strip()
    clean_word = "".join(c for c in word if c.isalpha() or c in "аеёиоуыэюяАЕЁИОУЫЭЮЯ")
    return [(clean_word, count_syllables(clean_word))]


def analyze_rhythm(line: str) -> dict:
    """Анализирует ритм строки.
    
    Args:
        line: Строка для анализа.
        
    Returns:
        Словарь с информацией о ритме:
        - total_syllables: общее количество слогов
        - words: список слов с количеством слогов
        - syllable_pattern: паттерн ударений (упрощённый)
    """
    words = line.strip().split()
    word_details = []
    total_syllables = 0
    
    for word in words:
        clean_word = "".join(c for c in word if c.isalpha() or c in "аеёиоуыэюяАЕЁИОУЫЭЮЯ")
        if clean_word:
            syllables = count_syllables(clean_word)
            word_details.append({
                "word": clean_word,
                "syllables": syllables
            })
            total_syllables += syllables
    
    return {
        "total_syllables": total_syllables,
        "words": word_details,
        "word_count": len(word_details)
    }


def check_meter_consistency(lines: list, expected_syllables: int = 8) -> dict:
    """Проверяет соответствие размеру (количеству слогов в строке).
    
    Args:
        lines: Список строк.
        expected_syllables: Ожидаемое количество слогов на строку.
        
    Returns:
        Словарь с результатами проверки:
        - consistent: все ли строки соответствуют размеру
        - deviations: отклонения от заданного размера
        - average_syllables: среднее количество слогов
    """
    deviations = []
    syllable_counts = []
    
    for i, line in enumerate(lines):
        if line.strip():
            count = count_line_syllables(line)
            syllable_counts.append(count)
            deviation = count - expected_syllables
            if abs(deviation) > 1:  # Допуск 1 слог
                deviations.append({
                    "line_num": i + 1,
                    "line": line.strip(),
                    "actual": count,
                    "expected": expected_syllables,
                    "deviation": deviation
                })
    
    average = sum(syllable_counts) / len(syllable_counts) if syllable_counts else 0
    
    return {
        "consistent": len(deviations) == 0,
        "deviations": deviations,
        "average_syllables": round(average, 1),
        "total_lines": len(syllable_counts),
        "matched_lines": len(syllable_counts) - len(deviations)
    }
