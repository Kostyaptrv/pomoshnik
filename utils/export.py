"""Утилиты для экспорта песен."""
import os
from typing import Optional

from engine.editor import get_song_stats

# Путь к шрифтам Windows для поддержки кириллицы
WINDOWS_FONTS = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")


def _get_font_path(name: str) -> str:
    """Возвращает путь к системному шрифту с поддержкой кириллицы."""
    candidates = {
        "Arial": ["arial.ttf", "ARIAL.TTF"],
        "Arial Bold": ["arialbd.ttf", "ARIALBD.TTF"],
        "Arial Italic": ["ariali.ttf", "ARIALI.TTF"],
        "Arial Bold Italic": ["arialbi.ttf", "ARIALBI.TTF"],
        "Times New Roman": ["times.ttf", "TIMES.TTF"],
        "Times New Roman Bold": ["timesbd.ttf", "TIMESBD.TTF"],
        "Times New Roman Italic": ["timesi.ttf", "TIMESI.TTF"],
        "Times New Roman Bold Italic": ["timesbi.ttf", "TIMESBI.TTF"],
    }
    for fname in candidates.get(name, []):
        path = os.path.join(WINDOWS_FONTS, fname)
        if os.path.exists(path):
            return path
    return ""


_FONT_REGISTERED = set()
_FONT_AVAILABLE = False


def _register_font(pdf, name: str, style_key: str, fname: str) -> bool:
    """Регистрирует шрифт в PDF один раз.
    
    Returns:
        True если шрифт успешно зарегистрирован, False иначе.
    """
    if fname in _FONT_REGISTERED:
        return True
    path = _get_font_path(fname)
    if path:
        pdf.add_font(name, style_key, path)
        _FONT_REGISTERED.add(fname)
        return True
    return False


def _check_font_availability() -> bool:
    """Проверяет, доступен ли хотя бы один шрифт с кириллицей."""
    return _FONT_AVAILABLE


def export_to_txt(song: dict) -> str:
    """Экспортирует песню в форматированный текст.

    Args:
        song: Словарь с песней.

    Returns:
        Строка с отформатированным текстом песни.
    """
    stats = get_song_stats(song)
    total_lines = stats["total_lines"]
    rhymed_lines = stats["rhymed_lines"]
    sections_filled = stats["sections_filled"]
    total_sections = len(song.get("sections", {}))
    rhyme_progress = (rhymed_lines / total_lines * 100) if total_lines > 0 else 0

    lines = [
        f"{'='*60}",
        f"  НАЗВАНИЕ: {song['title']}",
        f"  СТИЛЬ: {song.get('style_id', 'N/A').upper()}",
        f"  СОЗДАНО: {song.get('created_at', 'N/A')[:10]}",
        f"{'='*60}",
        "",
        "  📊 СТАТИСТИКА:",
        f"  • Заполнено секций: {sections_filled}/{total_sections}",
        f"  • Всего строк: {total_lines}",
        f"  • Рифмованных строк: {rhymed_lines}",
        f"  • Процент рифмы: {rhyme_progress:.1f}%",
        "",
        f"{'='*60}",
        "",
    ]

    for section_key, section_data in song.get("sections", {}).items():
        label = section_data.get("label", section_key)
        text = section_data.get("text", "").strip()
        section_type = section_data.get("type", "unknown")
        lines_hint = section_data.get("lines_hint", 0)

        lines.append(f"[{label}]")

        if text:
            for line_num, line in enumerate(text.split("\n"), 1):
                line = line.strip()
                if line:
                    lines.append(f"  {line_num}. {line}")
        else:
            lines.append("  (пусто)")

        if lines_hint > 0:
            lines.append(f"  💡 Рекомендация: ~{lines_hint} строк")

        lines.append("")

    return "\n".join(lines)


def export_to_pdf(song: dict, output_path: Optional[str] = None) -> bytes:
    """Экспортирует песню в PDF с поддержкой кириллицы.

    Args:
        song: Словарь с песней.
        output_path: Путь для сохранения (если None, возвращает bytes).

    Returns:
        Bytes PDF файла.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("Установите fpdf2 для экспорта в PDF: pip install fpdf2")

    stats = get_song_stats(song)
    total_lines = stats["total_lines"]
    rhymed_lines = stats["rhymed_lines"]
    sections_filled = stats["sections_filled"]
    total_sections = len(song.get("sections", {}))
    rhyme_progress = (rhymed_lines / total_lines * 100) if total_lines > 0 else 0

    pdf = FPDF()

    # Регистрируем шрифты с кириллицей
    global _FONT_AVAILABLE
    for fname in ["Arial", "Arial Bold", "Arial Italic", "Arial Bold Italic",
                  "Times New Roman", "Times New Roman Bold", "Times New Roman Italic", "Times New Roman Bold Italic"]:
        if _register_font(pdf, "Arial", "", "Arial"):
            _FONT_AVAILABLE = True
            break

    if not _FONT_AVAILABLE:
        raise RuntimeError(
            "Не найдены системные шрифты (Arial/Times New Roman) с поддержкой кириллицы. "
            "PDF будет содержать кракозябры. Убедитесь, что Windows имеет русскую локаль."
        )

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Заголовок
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, song["title"], align="C")
    pdf.ln(3)

    # Информация о песне
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Стиль: {song.get('style_id', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Создано: {song.get('created_at', 'N/A')[:10]}", new_x="LMARGIN", new_y="NEXT")

    # Статистика
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Статистика:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Заполнено секций: {sections_filled}/{total_sections}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Всего строк: {total_lines}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Рифмованных строк: {rhymed_lines}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Процент рифмы: {rhyme_progress:.1f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_text_color(0, 0, 0)

    # Секции песни
    for section_key, section_data in song.get("sections", {}).items():
        label = section_data.get("label", section_key)
        text = section_data.get("text", "").strip()
        section_type = section_data.get("type", "unknown")
        lines_hint = section_data.get("lines_hint", 0)
        tips = section_data.get("tips", [])

        # Заголовок секции
        pdf.set_font("Arial", "B", 12)
        pdf.ln(3)
        pdf.cell(0, 8, f"[{label}]", new_x="LMARGIN", new_y="NEXT")

        # Текст секции
        pdf.set_font("Times", "I", 11)
        if text:
            for line in text.split("\n"):
                line = line.strip()
                if line:
                    pdf.multi_cell(0, 6, line)
        else:
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, "(пусто)", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)

        # Подсказки
        if tips:
            pdf.ln(2)
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, "💡 Советы:", new_x="LMARGIN", new_y="NEXT")
            for tip in tips:
                pdf.cell(0, 5, f"   • {tip}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

    # Генерация PDF
    pdf_bytes = pdf.output()

    # Сохранение в файл если указан путь
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes


def get_export_formats() -> list[str]:
    """Возвращает доступные форматы экспорта.

    Returns:
        Список форматов.
    """
    return ["TXT", "PDF"]
