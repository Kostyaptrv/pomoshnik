"""Движок для редактирования и управления песнями."""
import json
import os
import uuid
from datetime import datetime
from typing import Optional

from engine.rhymes import get_rhymes

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "songs")
os.makedirs(STORAGE_DIR, exist_ok=True)


def _get_song_path(song_id: str) -> str:
    """Возвращает путь к файлу песни."""
    return os.path.join(STORAGE_DIR, f"{song_id}.json")


def create_song(title: str, style_id: str, template_context: dict) -> dict:
    """Создаёт новую песню.

    Args:
        title: Название песни.
        style_id: ID стиля.
        template_context: Контекст шаблона из structure.py.

    Returns:
        Словарь с созданной песней.
    """
    song_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()

    song = {
        "id": song_id,
        "title": title,
        "style_id": style_id,
        "created_at": now,
        "updated_at": now,
        "sections": template_context.get("sections", {}),
        "version": 1,
        "stats": {
            "total_lines": 0,
            "rhymed_lines": 0,
            "sections_filled": 0,
        },
    }

    song_path = _get_song_path(song_id)
    with open(song_path, "w", encoding="utf-8") as f:
        json.dump(song, f, ensure_ascii=False, indent=2)

    return song


def save_song(song: dict) -> bool:
    """Сохраняет песню на диск.

    Args:
        song: Словарь с данными песни.

    Returns:
        True если сохранение успешно.
    """
    song["updated_at"] = datetime.now().isoformat()
    song["version"] = song.get("version", 1) + 1

    song_path = _get_song_path(song["id"])
    with open(song_path, "w", encoding="utf-8") as f:
        json.dump(song, f, ensure_ascii=False, indent=2)

    return True


def load_song(song_id: str) -> Optional[dict]:
    """Загружает песню по ID.

    Args:
        song_id: ID песни.

    Returns:
        Словарь с песней или None.
    """
    song_path = _get_song_path(song_id)
    if not os.path.exists(song_path):
        return None

    with open(song_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_songs() -> list[dict]:
    """Получает список всех сохранённых песен.

    Returns:
        Список словарей с данными песен, включая статистику.
    """
    songs = []

    if not os.path.exists(STORAGE_DIR):
        return songs

    for filename in os.listdir(STORAGE_DIR):
        if filename.endswith(".json"):
            song_path = os.path.join(STORAGE_DIR, filename)
            with open(song_path, "r", encoding="utf-8") as f:
                song = json.load(f)
                song_entry = {
                    "id": song["id"],
                    "title": song["title"],
                    "style_id": song.get("style_id", ""),
                    "created_at": song.get("created_at", ""),
                    "updated_at": song.get("updated_at", ""),
                    "version": song.get("version", 1),
                    "stats": song.get("stats", {
                        "total_lines": 0,
                        "rhymed_lines": 0,
                        "sections_filled": 0,
                    }),
                }
                songs.append(song_entry)

    songs.sort(key=lambda s: s["updated_at"], reverse=True)
    return songs





def delete_song(song_id: str) -> bool:
    """Удаляет песню.

    Args:
        song_id: ID песни.

    Returns:
        True если удаление успешно.
    """
    song_path = _get_song_path(song_id)
    if os.path.exists(song_path):
        os.remove(song_path)
        return True
    return False


def clone_song(song_id: str) -> Optional[dict]:
    """Клонирует песню.

    Args:
        song_id: ID песни для клонирования.

    Returns:
        Словарь с клонированной песней или None.
    """
    song = load_song(song_id)
    if not song:
        return None

    import copy
    cloned = copy.deepcopy(song)
    cloned["id"] = str(uuid.uuid4())[:8]
    cloned["title"] = f"{song['title']} (копия)"
    cloned["created_at"] = datetime.now().isoformat()
    cloned["updated_at"] = datetime.now().isoformat()
    cloned["version"] = 1

    # Сохраняем клон
    song_path = _get_song_path(cloned["id"])
    with open(song_path, "w", encoding="utf-8") as f:
        json.dump(cloned, f, ensure_ascii=False, indent=2)

    return cloned


def get_song_text(song: dict) -> str:
    """Форматирует полный текст песни.

    Args:
        song: Словарь с песней.

    Returns:
        Отформатированный текст песни.
    """
    lines = [f"{'='*50}", f"НАЗВАНИЕ: {song['title']}", f"СТИЛЬ: {song.get('style_id', 'N/A')}", f"{'='*50}", ""]

    for section_key, section_data in song.get("sections", {}).items():
        label = section_data.get("label", section_key)
        text = section_data.get("text", "").strip()
        section_type = section_data.get("type", "unknown")

        lines.append(f"[{label}]")
        if text:
            lines.append(text)
        else:
            lines.append("(пусто)")
        lines.append("")

    return "\n".join(lines)


def update_section_text(song_id: str, section_key: str, text: str) -> bool:
    """Обновляет текст секции песни с пересчётом статистики.

    Args:
        song_id: ID песни.
        section_key: Ключ секции.
        text: Новый текст.

    Returns:
        True если обновление успешно.
    """
    song = load_song(song_id)
    if not song:
        return False

    if section_key in song["sections"]:
        song["sections"][section_key]["text"] = text
        _recalculate_stats(song)
        save_song(song)
        return True

    return False


def _recalculate_stats(song: dict) -> None:
    """Пересчитывает статистику песни.

    Args:
        song: Словарь с песней.
    """
    total_lines = 0
    rhymed_lines = 0
    sections_filled = 0

    # Кэш для get_rhymes — вызываем один раз на уникальное слово
    rhyme_cache = {}

    def get_rhyme_cached(word: str) -> list:
        if word not in rhyme_cache:
            rhyme_cache[word] = get_rhymes(word)
        return rhyme_cache[word]

    for section_key, section_data in song.get("sections", {}).items():
        text = section_data.get("text", "").strip()
        if text:
            sections_filled += 1
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            total_lines += len(lines)

            for line in lines:
                words = line.lower().split()
                if words:
                    last_word = words[-1].strip('.,!?;:")\']')
                    if get_rhyme_cached(last_word):
                        rhymed_lines += 1

    song["stats"] = {
        "total_lines": total_lines,
        "rhymed_lines": rhymed_lines,
        "sections_filled": sections_filled,
    }


def get_song_stats(song: dict) -> dict:
    """Получает статистику песни.

    Args:
        song: Словарь с песней.

    Returns:
        Словарь со статистикой.
    """
    if not song:
        return {"total_lines": 0, "rhymed_lines": 0, "sections_filled": 0}
    return song.get("stats", {
        "total_lines": 0,
        "rhymed_lines": 0,
        "sections_filled": 0,
    })
