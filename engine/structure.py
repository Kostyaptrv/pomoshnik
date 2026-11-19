"""Движок для работы с шаблонами песен."""
import json
import os
import sys
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(sys.executable), "data")


def _data_path(name: str) -> str:
    """Get path to data file, checking frozen app first."""
    applied_dir = os.path.dirname(sys.executable)
    
    if getattr(sys, 'frozen', False):
        candidate = os.path.join(applied_dir, "data", name)
        if os.path.exists(candidate):
            return candidate
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", name)
    if os.path.exists(src_dir):
        return src_dir
    return os.path.join(applied_dir, "data", name)


TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")


def _load_templates() -> dict:
    """Загрузка шаблонов из JSON файла."""
    templates_file = _data_path("templates.json")
    if not os.path.exists(templates_file):
        return {}
    try:
        with open(templates_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return {}


def get_available_styles() -> list[dict]:
    """Получает список доступных стилей.

    Returns:
        Список словарей с id, name и description каждого стиля.
    """
    templates = _load_templates()
    return [
        {"id": style_id, "name": data["name"], "description": data["description"]}
        for style_id, data in templates.items()
    ]


def get_template(style_id: str) -> Optional[dict]:
    """Получает полный шаблон для указанного стиля.

    Args:
        style_id: ID стиля (например, 'поп', 'рок', 'рэп').

    Returns:
        Словарь с шаблоном или None, если стиль не найден.
    """
    templates = _load_templates()
    if style_id not in templates:
        return None

    style_data = templates[style_id]
    return {
        "id": style_id,
        "name": style_data["name"],
        "description": style_data["description"],
        "structure": style_data["structure"],
    }


def create_template_context(style_id: str) -> dict:
    """Создаёт контекст для редактора на основе шаблона.

    Args:
        style_id: ID стиля.

    Returns:
        Словарь с контекстом редактора.
    """
    template = get_template(style_id)
    if not template:
        return {"error": "Шаблон не найден"}

    sections = {}
    for i, section in enumerate(template["structure"]):
        section_key = f"section_{i}"
        sections[section_key] = {
            "type": section["section"],
            "label": section["label"],
            "lines_hint": section.get("lines_hint", 4),
            "tips": section.get("tips", []),
            "text": "",
        }

    return {
        "style_id": style_id,
        "style_name": template["name"],
        "description": template["description"],
        "sections": sections,
        "total_sections": len(sections),
    }


def get_section_type_labels() -> dict:
    """Возвращает словарь с метками типов секций.

    Returns:
        Словарь с метками.
    """
    return {
        "куплет": "🎤 Куплет",
        "припев": "🔊 Припев",
        "бридж": "🌉 Бридж",
        "интро": "🎬 Интро",
        "проигрыш": "🎸 Проигрыш",
        "аутро": "🏁 Аутро",
    }
