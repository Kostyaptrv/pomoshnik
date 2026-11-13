"""Редактор песен — пошаговый мастер с редактированием секций."""

import uuid
import os
from datetime import datetime
from typing import Optional

from utils import logger as app_logger

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit, QFrame,
    QSplitter, QScrollArea, QGroupBox, QComboBox,
    QMessageBox, QProgressBar, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor, QTextFormat, QKeyEvent

from engine import editor
from engine import structure
from engine import syllable_counter
from engine import phrases as phrases_engine


class RhymeHighlighter(QSyntaxHighlighter):
    """Перекрёстная подсветка рифм — подсвечивает рифмующиеся слова между всеми строками."""

    RHYME_COLORS = [
        QColor(233, 69, 96),
        QColor(96, 165, 250),
        QColor(74, 222, 128),
        QColor(251, 191, 36),
        QColor(167, 139, 250),
        QColor(251, 146, 60),
        QColor(52, 211, 153),
        QColor(244, 114, 182),
    ]

    def __init__(self, document):
        super().__init__(document)
        self.rhyme_groups = []  # list of sets of words
        self.word_to_group = {}  # word_lower -> group_index
        self._updating = False
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._build_rhyme_map)
        self._update_formats()
        document.documentLayout().documentSizeChanged.connect(self._schedule_rebuild)

    def _update_formats(self):
        self.formats = []
        for color in self.RHYME_COLORS:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor(color.red(), color.green(), color.blue(), 50))
            fmt.setForeground(QColor(color.red(), color.green(), color.blue(), 220))
            fmt.setFontWeight(QFont.Weight.Bold)
            self.formats.append(fmt)

    def _extract_last_word(self, text: str) -> str:
        """Извлекает последнее значимое слово из строки."""
        words = text.strip().split()
        if not words:
            return ""
        return words[-1].strip(".,!?;:\"')\\]")

    def _schedule_rebuild(self):
        """Откладывает перестройку карты рифм на 400ms."""
        self._debounce_timer.start(400)

    def _build_rhyme_map(self, size=None):
        """Собирает все последние слова из документа и строит группы рифм."""
        if self._updating:
            return

        self._updating = True
        try:
            document = self.document()
            block = document.firstBlock()
            last_words = []  # list of (word_lower, original_word, block_number)

            block_num = 0
            while block.isValid():
                text = block.text()
                word = self._extract_last_word(text)
                if word and len(word) >= 3:
                    last_words.append((word.lower(), word, block_num))
                block = block.next()
                block_num += 1

            # Строим группы рифм
            self.rhyme_groups = []
            self.word_to_group = {}

            try:
                from engine import rhymes as rhyme_engine
            except Exception:
                self.rehighlight()
                return

            for word_lower, original_word, bnum in last_words:
                if word_lower in self.word_to_group:
                    continue

                try:
                    rhyme_list = rhyme_engine.get_rhymes(word_lower, max_results=10)
                except Exception:
                    continue

                if not rhyme_list:
                    continue

                # Ищем существующую группу
                group_index = -1
                for i, group in enumerate(self.rhyme_groups):
                    if word_lower in group or any(r in group for r in rhyme_list[:5]):
                        group_index = i
                        group.add(word_lower)
                        self.word_to_group[word_lower] = group_index
                        break

                if group_index == -1 and len(self.rhyme_groups) < len(self.RHYME_COLORS):
                    group = {word_lower}
                    for r in rhyme_list[:5]:
                        group.add(r.lower())
                    self.rhyme_groups.append(group)
                    self.word_to_group[word_lower] = len(self.rhyme_groups) - 1

            self.rehighlight()
        finally:
            self._updating = False

    def highlightBlock(self, text):
        if not text.strip():
            return

        last_word = self._extract_last_word(text)
        if not last_word or len(last_word) < 3:
            return

        word_lower = last_word.lower()
        group_index = self.word_to_group.get(word_lower)

        if group_index is not None and 0 <= group_index < len(self.formats):
            fmt = self.formats[group_index % len(self.formats)]
            start = text.rfind(last_word)
            if start >= 0:
                self.setFormat(start, len(last_word), fmt)


class TipsBox(QGroupBox):
    """Блок подсказок для текущей секции."""

    def __init__(self, parent=None):
        super().__init__("💡 Подсказки", parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.static_tips = QTextEdit()
        self.static_tips.setReadOnly(True)
        self.static_tips.setMaximumHeight(150)
        self.static_tips.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.static_tips)

        self.ai_tips = QTextEdit()
        self.ai_tips.setReadOnly(True)
        self.ai_tips.setMaximumHeight(150)
        self.ai_tips.setFont(QFont("Segoe UI", 10))
        self.ai_tips.setVisible(False)
        layout.addWidget(self.ai_tips)

    def set_static_tips(self, tips: list):
        if tips:
            text = "\n".join(f"• {tip}" for tip in tips)
            self.static_tips.setHtml(
                f"<div style='color: #b8b8d4; line-height: 1.6;'>{text}</div>"
            )
            self.static_tips.setVisible(True)
        else:
            self.static_tips.setVisible(False)

    def set_ai_suggestions(self, suggestions: list):
        if suggestions:
            text = "\n".join(f"• {s}" for s in suggestions)
            self.ai_tips.setHtml(
                f"<div style='color: #60a5fa; line-height: 1.6;'>{text}</div>"
            )
            self.ai_tips.setVisible(True)
        else:
            self.ai_tips.setVisible(False)


class EditorPage(QWidget):
    """Редактор песен — свободное редактирование секций."""

    song_saved = pyqtSignal()

    def __init__(self, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self.song: Optional[dict] = None
        self.template_context: Optional[dict] = None
        self.current_section_index = -1
        self._updating = False
        self._auto_save_timer: Optional[QTimer] = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 12, 16, 12)

        # Заглушка
        self.empty_state = QLabel("📄 Выберите шаблон на странице «Шаблоны песен»")
        self.empty_state.setFont(QFont("Segoe UI", 14))
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setStyleSheet("color: #b8b8d4; padding: 100px;")
        main_layout.addWidget(self.empty_state)
        main_layout.addStretch()

        # Верхняя панель
        self.top_panel = QWidget()
        top_layout = QHBoxLayout(self.top_panel)
        top_layout.setSpacing(12)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название песни...")
        self.title_input.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.title_input.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 8px 12px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #e94560;
            }
        """)
        top_layout.addWidget(self.title_input, 1)

        save_btn = QPushButton("💾 &Сохранить")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._manual_save)
        top_layout.addWidget(save_btn)

        export_btn = QPushButton("📄 &Экспорт PDF")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._export_pdf)
        top_layout.addWidget(export_btn)

        preview_btn = QPushButton("👁 &Предпросмотр")
        preview_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        preview_btn.clicked.connect(self._preview_song)
        top_layout.addWidget(preview_btn)

        import_btn = QPushButton("📂 &Импорт")
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.clicked.connect(self._import_text)
        top_layout.addWidget(import_btn)

        ai_btn = QPushButton("🤖 &Генерация")
        ai_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ai_btn.clicked.connect(self._ai_generate)
        top_layout.addWidget(ai_btn)

        new_btn = QPushButton("📄 Новая песня")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self._new_song)
        top_layout.addWidget(new_btn)

        main_layout.addWidget(self.top_panel)
        self.top_panel.setVisible(False)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #16213e;
                border: none;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e94560, stop:1 #0f3460);
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Статистика
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        self.sections_filled_label = QLabel("Заполнено: 0/0 секций")
        self.sections_filled_label.setFont(QFont("Segoe UI", 10))
        self.sections_filled_label.setStyleSheet("color: #b8b8d4;")
        stats_layout.addWidget(self.sections_filled_label)

        self.lines_count_label = QLabel("Строк: 0")
        self.lines_count_label.setFont(QFont("Segoe UI", 10))
        self.lines_count_label.setStyleSheet("color: #b8b8d4;")
        stats_layout.addWidget(self.lines_count_label)

        self.rhymes_count_label = QLabel("Рифм: 0")
        self.rhymes_count_label.setFont(QFont("Segoe UI", 10))
        self.rhymes_count_label.setStyleSheet("color: #b8b8d4;")
        stats_layout.addWidget(self.rhymes_count_label)

        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)

        # Сплиттер
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sections_panel = self._create_sections_panel()
        splitter.addWidget(self.sections_panel)

        self.editor_panel = self._create_editor_panel()
        splitter.addWidget(self.editor_panel)

        self.tips_panel = self._create_tips_panel()
        splitter.addWidget(self.tips_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)

        main_layout.addWidget(splitter, 1)

        self._auto_save_timer = QTimer()
        self._auto_save_timer.setInterval(5000)
        self._auto_save_timer.timeout.connect(self._auto_save)

        self._is_dirty = False

    def _create_sections_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("card_frame")
        panel.setStyleSheet("""
            QWidget#card_frame {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        heading = QLabel("📑 Секции")
        heading.setObjectName("heading_label")
        layout.addWidget(heading)

        self.sections_list = QListWidget()
        self.sections_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.sections_list.setIconSize(QSize(24, 24))
        self.sections_list.setSpacing(6)
        self.sections_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 8px;
                margin: 2px 0;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: #1f2b4d;
            }
            QListWidget::item:selected {
                background-color: #1f2b4d;
            }
        """)

        layout.addWidget(self.sections_list)
        self.sections_list.itemClicked.connect(self._on_section_clicked)

        return panel

    def _create_editor_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("card_frame")
        panel.setStyleSheet("""
            QWidget#card_frame {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(10)

        self.section_type_label = QLabel("🎤 Тип секции")
        self.section_type_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.section_type_label.setStyleSheet("color: #e94560;")
        info_layout.addWidget(self.section_type_label)

        self.section_label = QLabel("Название")
        self.section_label.setFont(QFont("Segoe UI", 12))
        self.section_label.setStyleSheet("color: #ffffff;")
        info_layout.addWidget(self.section_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier New", 11))
        self.text_edit.setPlaceholderText(
            "Введите текст секции...\n\n"
            "Каждая строка — отдельная строка куплета или припева."
        )
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                border: 2px solid #2a2a4a;
                border-radius: 10px;
                padding: 12px;
                color: #ffffff;
                selection-background-color: #e94560;
            }
            QTextEdit:focus {
                border-color: #e94560;
            }
        """)
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.installEventFilter(self)

        self.rhyme_highlighter = RhymeHighlighter(self.text_edit.document())

        layout.addWidget(self.text_edit)

        self.line_count_label = QLabel("Строк: 0 | Слогов: 0")
        self.line_count_label.setFont(QFont("Segoe UI", 9))
        self.line_count_label.setStyleSheet("color: #6c6c8a;")
        layout.addWidget(self.line_count_label)

        layout.addStretch()
        return panel

    def _create_tips_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("card_frame")
        panel.setStyleSheet("""
            QWidget#card_frame {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        heading = QLabel("💡 Подсказки")
        heading.setObjectName("heading_label")
        layout.addWidget(heading)

        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(6)

        self.tips_mode_combo = QComboBox()
        self.tips_mode_combo.addItems(["Статические", "Генерация", "Обе"])
        self.tips_mode_combo.currentIndexChanged.connect(self._update_tips_display)
        mode_layout.addWidget(self.tips_mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        self.tips_box = TipsBox()
        layout.addWidget(self.tips_box)

        layout.addStretch()
        return panel

    def _has_unsaved_changes(self) -> bool:
        """Проверяет, есть ли несохранённые изменения."""
        return self._is_dirty

    def set_template(self, style_id: str):
        self._is_dirty = False
        self._updating = False
        self.template_context = structure.create_template_context(style_id)
        if "error" in self.template_context:
            QMessageBox.critical(self, "Ошибка", f"Шаблон '{style_id}' не найден")
            return

        title = f"Новая песня ({self.template_context['style_name']})"
        self.song = editor.create_song(
            title=title,
            style_id=style_id,
            template_context=self.template_context
        )

        self.title_input.setText(self.song["title"])
        self._build_sections_list()
        self._go_to_section(0)
        self._start_auto_save()
        self._show_editor()

        if hasattr(self, 'rhyme_highlighter'):
            self.rhyme_highlighter._build_rhyme_map()

        self._toast("success", f"Песня '{title}' создана!")
        app_logger.logger.info(f"Создана новая песня: {title}")

    def load_existing_song(self, song: dict):
        # Проверяем несохранённые изменения
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self, "Несохранённые изменения",
                "Есть несохранённые изменения. Загрузить другую песню?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._stop_auto_save()
        self._is_dirty = False
        self._updating = False
        self.song = song
        self.template_context = structure.create_template_context(song.get("style_id", "поп"))
        if "error" not in self.template_context:
            self.title_input.setText(song["title"])
            self._build_sections_list()
            self._go_to_section(0)
            self._start_auto_save()
            self._show_editor()

            if hasattr(self, 'rhyme_highlighter'):
                self.rhyme_highlighter._build_rhyme_map()

    def _show_editor(self):
        self.empty_state.setVisible(False)
        self.top_panel.setVisible(True)

    def _build_sections_list(self):
        self.sections_list.clear()
        self.section_items = []
        self.current_section_index = -1
        self._is_dirty = False
        sections = self.template_context["sections"]

        for index, (section_key, section_data) in enumerate(sections.items()):
            label = section_data["label"]
            item = QListWidgetItem(f"○ {label}")
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.sections_list.addItem(item)
            self.section_items.append(item)

        self._update_sections_list()

    def _on_section_clicked(self, item: QListWidgetItem):
        index = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(index, int):
            self._go_to_section(index)

    def _go_to_section(self, index: int):
        if not hasattr(self, "section_items") or not self.song or not self.template_context:
            return

        if self.current_section_index >= 0:
            self._save_current_section_text()

        self.current_section_index = index
        sections = self.song["sections"]
        section_keys = list(sections.keys())
        section_key = section_keys[index]
        section_data = sections[section_key]

        for i, item in enumerate(self.section_items):
            if i == index:
                item.setBackground(Qt.GlobalColor.darkGray)
            else:
                item.setBackground(Qt.GlobalColor.transparent)

        template_sections = self.template_context["sections"]
        template_section = template_sections[section_key]
        section_type = template_section.get("type", "unknown")

        self.section_type_label.setText(
            self._get_section_icon(section_type) + " " + section_type.title()
        )
        self.section_label.setText(section_data.get("label", section_key))
        self.text_edit.setPlainText(section_data.get("text", ""))

        self._update_tips()
        self._update_line_count()

    def _save_current_section_text(self):
        if not self.song or self.current_section_index < 0:
            return

        sections = self.song["sections"]
        section_keys = list(sections.keys())
        if 0 <= self.current_section_index < len(section_keys):
            section_key = section_keys[self.current_section_index]
            text = self.text_edit.toPlainText()
            sections[section_key]["text"] = text

    def _on_text_changed(self):
        if self._updating:
            return

        self._is_dirty = True
        self._updating = True
        try:
            self._update_line_count()
            self._update_sections_list()
            self._update_stats()

            if hasattr(self, 'rhyme_highlighter'):
                self.rhyme_highlighter._schedule_rebuild()
        finally:
            self._updating = False

    def _update_line_count(self):
        text = self.text_edit.toPlainText()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        line_count = len(lines)

        total_syllables = sum(syllable_counter.count_line_syllables(line) for line in lines)
        avg_syllables = total_syllables / line_count if line_count > 0 else 0

        self.line_count_label.setText(
            f"Строк: {line_count} | Слогов: {total_syllables} | Ср: {avg_syllables:.1f}"
        )

    def _update_sections_list(self):
        if not hasattr(self, "section_items"):
            return

        sections = self.song["sections"]
        section_keys = list(sections.keys())

        for i, item in enumerate(self.section_items):
            if i < len(section_keys):
                section_key = section_keys[i]
                text = sections[section_key].get("text", "").strip()
                filled = bool(text)
                label = item.text().split(" ", 1)[-1] if " " in item.text() else item.text()
                icon = "●" if filled else "○"
                item.setText(f"{icon} {label}")
                item.setForeground(Qt.GlobalColor.darkGreen if filled else Qt.GlobalColor.gray)

    def _update_stats(self):
        if not self.song:
            return

        sections = self.song["sections"]
        total = len(sections)
        filled = sum(1 for s in sections.values() if s.get("text", "").strip())

        total_lines = 0
        rhymed_lines = 0
        for section_data in sections.values():
            text = section_data.get("text", "").strip()
            if text:
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                total_lines += len(lines)
                for line in lines:
                    words = line.lower().split()
                    if words:
                        last_word = words[-1].strip(".,!?;:\"')\\]")
                        if last_word:
                            rhymed_lines += 1

        self.sections_filled_label.setText(f"Заполнено: {filled}/{total} секций")
        self.lines_count_label.setText(f"Строк: {total_lines}")
        self.rhymes_count_label.setText(f"Рифм: {rhymed_lines}")

        progress = int((filled / total * 100)) if total > 0 else 0
        self.progress_bar.setValue(progress)

    def _update_tips(self):
        if not self.template_context or self.current_section_index < 0:
            return

        sections = self.song["sections"]
        section_keys = list(sections.keys())
        if self.current_section_index >= len(section_keys):
            return

        section_key = section_keys[self.current_section_index]
        template_sections = self.template_context["sections"]
        tips = template_sections[section_key].get("tips", [])
        self.tips_box.set_static_tips(tips)

        self._generate_ai_suggestions()

    def _generate_ai_suggestions(self):
        text = self.text_edit.toPlainText()
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        suggestions = []

        if lines:
            last_word = lines[-1].split()[-1].strip(".,!?;:\"')\\]")
            if last_word and len(last_word) > 2:
                from engine import rhymes
                rhyme_list = rhymes.get_rhymes(last_word, max_results=5)
                if rhyme_list:
                    suggestions.append(f"Рифмы к '{last_word}': {', '.join(rhyme_list[:5])}")

        random_phrases = phrases_engine.get_random_phrases(count=3)
        if random_phrases:
            suggestions.append(
                "Случайные фразы: " + " | ".join(random_phrases[:3])
            )

        mode = self.tips_mode_combo.currentText()
        if mode == "Статические":
            self.tips_box.set_ai_suggestions([])
        elif mode == "Генерация":
            self.tips_box.set_ai_suggestions(suggestions)
        else:
            self.tips_box.set_ai_suggestions(suggestions)

    def _update_tips_display(self):
        self._update_tips()

    def _toast(self, level: str, message: str):
        from ui.main_window import MainWindow
        parent = self.window()
        if isinstance(parent, MainWindow) and hasattr(parent, 'toast_manager'):
            parent.toast_manager.show(message, level)

    def _manual_save(self):
        self._save_current_section_text()
        if editor.save_song(self.song):
            self._is_dirty = False
            self._toast("success", "Песня успешно сохранена!")
            self.song_saved.emit()
            app_logger.logger.info(f"Песня сохранена: {self.song['title']}")

    def _auto_save(self):
        if not self._is_dirty:
            return
        self._save_current_section_text()
        editor.save_song(self.song)
        self._is_dirty = False

    def _start_auto_save(self):
        self._stop_auto_save()
        self._auto_save_timer.start()

    def _stop_auto_save(self):
        if self._auto_save_timer and self._auto_save_timer.isActive():
            self._auto_save_timer.stop()

    def _new_song(self):
        if self.song and self.song["sections"]:
            has_content = any(
                s.get("text", "").strip()
                for s in self.song["sections"].values()
            )
            if has_content:
                reply = QMessageBox.question(
                    self, "Новая песня",
                    "Создать новую песню? Текущий прогресс будет потерян.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

        self._stop_auto_save()

        self.song = None
        self.template_context = None
        self.title_input.clear()
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.sections_filled_label.setText("Заполнено: 0/0 секций")
        self.lines_count_label.setText("Строк: 0")
        self.rhymes_count_label.setText("Рифм: 0")

        if hasattr(self, "section_items"):
            for item in self.section_items:
                item.deleteLater()
            self.section_items.clear()

    def _export_pdf(self):
        if not self.song:
            self._toast("warning", "Сначала создайте или загрузите песню")
            return

        from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
        from PyQt6.QtCore import Qt
        from utils.export import export_to_pdf
        import threading

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в PDF", f"{self.song['title']}.pdf", "PDF файлы (*.pdf)"
        )

        if output_path:
            # Показываем прогресс-бар
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Экспорт в PDF")
            progress_dialog.setFixedSize(400, 150)
            progress_dialog.setWindowFlags(progress_dialog.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

            layout = QVBoxLayout(progress_dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            status_label = QLabel("Генерация PDF...")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setFont(QFont("Segoe UI", 11))
            layout.addWidget(status_label)

            progress_bar = QProgressBar()
            progress_bar.setFixedHeight(8)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #16213e;
                    border: none;
                    border-radius: 4px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #e94560, stop:1 #0f3460);
                    border-radius: 4px;
                }
            """)
            progress_bar.setValue(0)
            layout.addWidget(progress_bar)

            cancel_btn = QPushButton("Отмена")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.clicked.connect(progress_dialog.reject)
            layout.addWidget(cancel_btn)

            progress_dialog.show()

            # Флаг отмены
            cancel_flag = [False]

            def export_thread():
                try:
                    progress_dialog.repaint()
                    status_label.setText("Подготовка данных...")
                    progress_bar.setValue(30)

                    export_to_pdf(self.song, output_path)

                    progress_bar.setValue(80)
                    status_label.setText("Сохранение файла...")

                    progress_bar.setValue(100)
                    status_label.setText("Готово!")

                    # Успех
                    progress_dialog.accept()
                    self._toast("success", "Песня экспортирована в PDF!")
                    app_logger.logger.info(f"PDF экспортирован: {output_path}")
                except Exception as e:
                    if not cancel_flag[0]:
                        progress_bar.setValue(0)
                        status_label.setText(f"Ошибка!")
                        progress_dialog.reject()
                        app_logger.logger.error(f"Ошибка экспорта PDF: {e}")
                        self._toast("error", f"Ошибка экспорта: {str(e)}")

            thread = threading.Thread(target=export_thread)
            thread.daemon = True
            thread.start()

            progress_dialog.exec()
            thread.join()

    def _preview_song(self):
        if not self.song:
            self._toast("warning", "Сначала создайте или загрузите песню")
            return

        from ui.pages.preview_dialog import PreviewDialog
        dialog = PreviewDialog(self.song, self)
        dialog.exec()

    def _import_text(self):
        if not self.song:
            self._toast("warning", "Сначала создайте или загрузите песню")
            return

        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт текста", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                self.text_edit.setPlainText(text)
                self._on_text_changed()
                self._toast("success", "Текст импортирован!")
            except Exception as e:
                self._toast("error", f"Ошибка импорта: {str(e)}")

    def _ai_generate(self):
        import random

        if not self.song or self.current_section_index < 0:
            self._toast("warning", "Сначала создайте или загрузите песню")
            return

        sections = self.song["sections"]
        section_keys = list(sections.keys())
        section_key = section_keys[self.current_section_index]
        section_data = sections[section_key]
        template_sections = self.template_context["sections"]
        template_section = template_sections[section_key]

        tips = template_section.get("tips", [])
        section_type = template_section.get("type", "")
        lines_hint = section_data.get("lines_hint", 4)

        current_text = self.text_edit.toPlainText()
        current_lines = [l.strip() for l in current_text.split("\n") if l.strip()]

        generated_lines = self._generate_lines(section_type, current_lines, tips, lines_hint)

        if generated_lines:
            if current_text.strip():
                new_text = current_text + "\n" + "\n".join(generated_lines)
            else:
                new_text = "\n".join(generated_lines)

            self.text_edit.setPlainText(new_text)
            self._on_text_changed()
            self._toast("success", f"Сгенерировано {len(generated_lines)} строк!")
        else:
            self._toast("warning", "Не удалось сгенерировать текст. Заполните хотя бы одну строку.")

    def _generate_lines(self, section_type: str, current_lines: list, tips: list, lines_hint: int) -> list:
        import random
        from engine import phrases as phrases_engine
        from engine import rhymes

        generated = []
        target_lines = min(lines_hint, 8)

        # Собираем все доступные рифмы из текущего текста
        all_rhymes = {}  # {word: [rhymes]}
        for line in current_lines:
            words = line.split()
            if words:
                last_word = words[-1].strip(".,!?;:\"')\\]")
                if len(last_word) > 2:
                    rhyme_list = rhymes.get_rhymes(last_word, max_results=10)
                    if rhyme_list:
                        all_rhymes[last_word.lower()] = rhyme_list

        # Определяем схему рифмовки по текущему тексту
        rhyme_scheme = self._detect_rhyme_scheme(current_lines)

        # Получаем фразы по категории секции
        category_map = {
            "куплет": ["love", "nature", "pain", "hope"],
            "припев": ["love", "hope", "dreams"],
            "бридж": ["pain", "hope", "time"],
            "интро": ["nature", "dreams"],
            "проигрыш": [],
            "аутро": ["hope", "time"],
        }

        categories = category_map.get(section_type, ["love", "hope"])
        available_phrases = []
        for cat in categories:
            available_phrases.extend(phrases_engine.get_phrases_by_category(cat))

        # Уникальные рифмы для использования
        rhyme_pool = []
        for rhymes_list in all_rhymes.values():
            rhyme_pool.extend(rhymes_list)
        rhyme_pool = list(set(rhyme_pool))

        for i in range(target_lines):
            line_num = i + 1

            # Чётные строки (1, 3, 5...) — берём фразу
            # Нечётные (2, 4, 6...) — рифмуем к предыдущей
            if line_num % 2 == 0 and generated:
                # Рифмуем к предыдущей строке
                prev_line = generated[-1]
                prev_words = prev_line.split()
                if prev_words:
                    prev_end = prev_words[-1].strip(".,!?;:\"')\\]")
                    # Ищем рифму к предыдущей строке
                    target_rhymes = rhymes.get_rhymes(prev_end.lower(), max_results=8)

                    if target_rhymes and available_phrases:
                        # Комбинируем: фраза + рифма
                        phrase = random.choice(available_phrases)
                        rhyme = random.choice(target_rhymes)
                        words = phrase.split()
                        if len(words) > 2:
                            # Заменяем последнее слово на рифму
                            new_line = " ".join(words[:-1]) + " " + rhyme
                            generated.append(new_line)
                        else:
                            generated.append(rhyme)
                    elif target_rhymes:
                        generated.append(random.choice(target_rhymes))
                    elif available_phrases:
                        generated.append(random.choice(available_phrases))
                    else:
                        generated.append(self._make_filler_line(section_type))
                else:
                    generated.append(self._make_filler_line(section_type))
            else:
                # Новая строка — берём фразу или рифму
                if available_phrases and random.random() > 0.3:
                    generated.append(random.choice(available_phrases))
                elif rhyme_pool:
                    generated.append(random.choice(rhyme_pool))
                elif tips:
                    tip = random.choice(tips)
                    generated.append(self._make_tip_line(tip))
                else:
                    generated.append(self._make_filler_line(section_type))

        return generated

    def _detect_rhyme_scheme(self, lines: list) -> str:
        """Определяет схему рифмовки по текущему тексту."""
        if len(lines) < 4:
            return "AABB"

        # Получаем последние слова
        last_words = []
        for line in lines:
            words = line.split()
            if words:
                last_word = words[-1].strip(".,!?;:\"')\\]").lower()
                last_words.append(last_word)

        if len(last_words) < 4:
            return "AABB"

        # Проверяем AABB (1=2, 3=4)
        aabb = (last_words[0] == last_words[1] or self._are_rhymes(last_words[0], last_words[1])) and \
               (last_words[2] == last_words[3] or self._are_rhymes(last_words[2], last_words[3]))

        # Проверяем ABAB (1=3, 2=4)
        abab = (last_words[0] == last_words[2] or self._are_rhymes(last_words[0], last_words[2])) and \
               (last_words[1] == last_words[3] or self._are_rhymes(last_words[1], last_words[3]))

        if aabb:
            return "AABB"
        if abab:
            return "ABAB"

        return "AABB"  # По умолчанию

    def _are_rhymes(self, word1: str, word2: str) -> bool:
        """Проверяет, рифмуются ли два слова."""
        try:
            from engine import rhymes
            rhymes_list = rhymes.get_rhymes(word1, max_results=5)
            return word2 in rhymes_list
        except Exception:
            return False

    def _make_filler_line(self, section_type: str) -> str:
        """Создает осмысленную filler-строку для секции."""
        fillers = {
            "куплет": [
                "В тишине звучат старые слова",
                "Мечты летят сквозь время и простор",
                "Сердце ищет свой единственный путь",
                "Тени прошлого касаются огня",
            ],
            "припев": [
                "И я пою тебе эту песню",
                "Это наше общее небо",
                "Мы одни на этом свете",
                "Ты и я — одна история",
            ],
            "бридж": [
                "Всё меняется, но чувства остаются",
                "За горизонтом начинается новый день",
                "Это последний шанс сказать",
            ],
            "интро": [
                "Ветер приносит звуки далёких мест",
                "Ночь опускается на пустой город",
            ],
            "аутро": [
                "И всё затихает навсегда",
                "Эхо разносится по пустым улицам",
            ],
            "проигрыш": [],
        }

        lines = fillers.get(section_type, fillers["куплет"])
        if lines:
            return random.choice(lines)
        return "Звучит музыка..."

    def _make_tip_line(self, tip: str) -> str:
        """Создает строку на основе подсказки."""
        return f"Вдохновлённый: {tip}"

    def eventFilter(self, obj, event):
        if obj == self.text_edit and isinstance(event, QKeyEvent):
            # Ctrl+S — сохранение
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
                self._manual_save()
                return True
            # Ctrl+E — экспорт PDF
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_E:
                self._export_pdf()
                return True
            # Ctrl+P — предпросмотр
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_P:
                self._preview_song()
                return True
            # Ctrl+F — поиск
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_F:
                self._show_find_dialog()
                return True
            # Ctrl+Z — отмена
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Z:
                self.text_edit.undo()
                return True
            # Ctrl+Y — повтор
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Y:
                self.text_edit.redo()
                return True
        return super().eventFilter(obj, event)

    def _show_find_dialog(self):
        """Показывает диалог поиска по тексту."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Поиск")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Найти:"))
        find_input = QLineEdit()
        find_input.setPlaceholderText("Введите текст для поиска...")
        search_layout.addWidget(find_input)
        layout.addLayout(search_layout)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Найти")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(lambda: self._perform_find(find_input.text(), dialog))
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        find_input.setFocus()
        dialog.exec()

    def _perform_find(self, query: str, dialog):
        """Выполняет поиск текста."""
        if not query.strip():
            return

        text = self.text_edit.toPlainText()
        idx = text.find(query)
        if idx >= 0:
            cursor = self.text_edit.textCursor()
            cursor.setPosition(idx)
            cursor.select(cursor.TextUnderCursor)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.ensureCursorVisible()
            self._toast("info", f"Найдено в позиции {idx + 1}")
        else:
            self._toast("warning", f"Не найдено: '{query}'")

    def _get_section_icon(self, section_type: str) -> str:
        icons = {
            "куплет": "🎤",
            "припев": "🔊",
            "бридж": "🌉",
            "интро": "🎬",
            "проигрыш": "🎸",
            "аутро": "🏁",
        }
        return icons.get(section_type, "🎵")

    def closeEvent(self, event):
        if self.song:
            self._save_current_section_text()
            editor.save_song(self.song)
        event.accept()
