"""Страница списка песен."""

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QFrame, QMessageBox, QTabWidget, QSplitter, QComboBox, QLineEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from engine import editor


class SongCard(QFrame):
    """Карточка песни."""

    def __init__(self, song_data: dict, parent=None):
        super().__init__(parent)
        self.song_data = song_data
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Заголовок
        title = QLabel(self.song_data["title"])
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        # Метаданные
        meta_layout = QHBoxLayout()
        style = self.song_data.get("style_id", "N/A")
        updated = self.song_data.get("updated_at", "")

        style_label = QLabel(f"🎵 {style}")
        style_label.setFont(QFont("Segoe UI", 10))
        style_label.setStyleSheet("color: #e94560;")
        meta_layout.addWidget(style_label)

        date_label = QLabel(f"📅 {updated[:10] if updated else 'N/A'}")
        date_label.setFont(QFont("Segoe UI", 10))
        date_label.setStyleSheet("color: #6c6c8a;")
        meta_layout.addWidget(date_label)
        meta_layout.addStretch()
        layout.addLayout(meta_layout)

        # Статистика
        stats = self.song_data.get("stats", {
            "total_lines": 0,
            "rhymed_lines": 0,
            "sections_filled": 0,
        })
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        for value, label in [
            (str(stats.get("total_lines", 0)), "строк"),
            (str(stats.get("rhymed_lines", 0)), "рифм"),
            (str(stats.get("sections_filled", 0)), "секций"),
        ]:
            val_label = QLabel(value)
            val_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            val_label.setStyleSheet("color: #4ade80;")
            stats_layout.addWidget(val_label)

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 9))
            lbl.setStyleSheet("color: #b8b8d4;")
            stats_layout.addWidget(lbl)

        layout.addLayout(stats_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        view_btn = QPushButton("👁 &Просмотр")
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.clicked.connect(self._view_song)
        btn_layout.addWidget(view_btn)

        edit_btn = QPushButton("✏️ &Редактировать")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(self._edit_song)
        btn_layout.addWidget(edit_btn)

        rename_btn = QPushButton("✏️ &Переименовать")
        rename_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rename_btn.clicked.connect(self._rename_song)
        btn_layout.addWidget(rename_btn)

        delete_btn = QPushButton("🗑 &Удалить")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self._delete_song)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #e94560;
            }
        """)

    def _view_song(self):
        """Показывает текст песни."""
        song = editor.load_song(self.song_data["id"])
        if song:
            text = editor.get_song_text(song)
            QMessageBox.information(
                self, f"Песня: {song['title']}",
                text
            )

    def _edit_song(self):
        """Открывает песню в редакторе."""
        from ui.main_window import MainWindow
        parent = self.window()
        if isinstance(parent, MainWindow):
            editor_page = parent.get_editor_page()
            if editor_page:
                # Загружаем песню в редактор
                song = editor.load_song(self.song_data["id"])
                if song:
                    editor_page.load_existing_song(song)
                    # Переключаемся на страницу редактора
                    idx = parent._get_page_index("editor")
                    if idx >= 0:
                        parent.stacked.setCurrentIndex(idx)
                        parent.nav_list.setCurrentRow(idx)

    def _rename_song(self):
        """Переименовывает песню."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Переименовать песню")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Новое название:"))
        name_input = QLineEdit()
        name_input.setText(self.song_data["title"])
        layout.addWidget(name_input)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(lambda: self._save_rename(name_input.text(), dialog))
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        name_input.setFocus()
        dialog.exec()

    def _save_rename(self, new_name: str, dialog):
        """Сохраняет новое название песни."""
        if not new_name.strip():
            QMessageBox.warning(self, "Ошибка", "Введите название песни")
            return

        song = editor.load_song(self.song_data["id"])
        if not song:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить песню")
            return

        old_title = song["title"]
        song["title"] = new_name.strip()
        editor.save_song(song)

        self.song_data["title"] = new_name.strip()
        self.deleted.emit()

        QMessageBox.information(
            self, "Готово",
            f"Песня переименована:\n{old_title} → {new_name.strip()}"
        )
        dialog.accept()

    def _delete_song(self):
        """Удаляет песню."""
        reply = QMessageBox.question(
            self, "Удаление",
            f"Удалить песню '{self.song_data['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if editor.delete_song(self.song_data["id"]):
                QMessageBox.information(self, "Удалено", "Песня удалена!")
                self.deleted.emit()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить песню")

    deleted = pyqtSignal()


class SongsPage(QWidget):
    """Страница списка песен."""

    song_deleted = pyqtSignal()

    def __init__(self, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self._init_ui()
        self._refresh_songs()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("🎶 Мои песни")
        title.setObjectName("heading_label")
        layout.addWidget(title)

        subtitle = QLabel("Управление вашими песнями")
        subtitle.setObjectName("subheading_label")
        layout.addWidget(subtitle)

        # Панель управления
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по названию...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self._refresh_songs)
        control_layout.addWidget(self.search_input)

        # Фильтр по жанру
        self.genre_filter = QComboBox()
        self.genre_filter.addItem("Все жанры")
        genres = sorted(set(s.get("style_id", "") for s in editor.get_all_songs() if s.get("style_id")))
        self.genre_filter.addItems(genres)
        self.genre_filter.currentTextChanged.connect(self._refresh_songs)
        control_layout.addWidget(self.genre_filter)

        # Сортировка
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По дате (новые)", "По дате (старые)", "По названию (А-Я)", "По названию (Я-А)"])
        self.sort_combo.currentTextChanged.connect(self._refresh_songs)
        control_layout.addWidget(self.sort_combo)

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self._refresh_songs)
        control_layout.addWidget(refresh_btn)

        layout.addLayout(control_layout)

        # Список песен
        self.songs_list = QListWidget()
        self.songs_list.itemDoubleClicked.connect(self._on_song_double_click)
        self.songs_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.songs_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.songs_list)

    def _refresh_songs(self):
        """Обновляет список песен с учётом фильтра и сортировки."""
        self.songs_list.clear()
        songs = editor.get_all_songs()

        # Поиск
        query = self.search_input.text().strip().lower()
        if query:
            songs = [s for s in songs if query in s["title"].lower()]

        # Фильтр по жанру
        genre = self.genre_filter.currentText()
        if genre and genre != "Все жанры":
            songs = [s for s in songs if s.get("style_id") == genre]

        # Сортировка
        sort_mode = self.sort_combo.currentText()
        if sort_mode == "По дате (новые)":
            songs.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        elif sort_mode == "По дате (старые)":
            songs.sort(key=lambda s: s.get("updated_at", ""))
        elif sort_mode == "По названию (А-Я)":
            songs.sort(key=lambda s: s["title"])
        elif sort_mode == "По названию (Я-А)":
            songs.sort(key=lambda s: s["title"], reverse=True)

        if not songs:
            self.songs_list.addItem("📭 Нет сохранённых песен")
            return

        for song in songs:
            item = QListWidgetItem(f"🎵 {song['title']}")
            item.setData(Qt.ItemDataRole.UserRole, song)
            self.songs_list.addItem(item)

    def _show_context_menu(self, position):
        """Показывает контекстное меню."""
        from PyQt6.QtWidgets import QMenu
        item = self.songs_list.itemAt(position)
        if not item:
            return

        song_data = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(song_data, dict):
            return

        menu = QMenu()

        # Действие: Просмотр
        view_action = menu.addAction("👁 Просмотреть")
        view_action.triggered.connect(lambda: self._view_song(song_data))

        # Действие: Редактировать
        edit_action = menu.addAction("✏️ Редактировать")
        edit_action.triggered.connect(lambda: self._edit_song_from_list(song_data))

        # Действие: Клонировать
        clone_action = menu.addAction("📋 Клонировать")
        clone_action.triggered.connect(lambda: self._clone_song(song_data))

        # Действие: Скачать текст
        download_action = menu.addAction("📥 Скачать текст")
        download_action.triggered.connect(lambda: self._download_txt(song_data))

        # Действие: Удалить
        delete_action = menu.addAction("🗑 Удалить")
        delete_action.triggered.connect(lambda: self._delete_song_from_list(song_data))

        menu.exec(self.songs_list.viewport().mapToGlobal(position))

    def _on_song_double_click(self, item: QListWidgetItem):
        """Обработка двойного клика по песне."""
        song_data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(song_data, dict):
            self._edit_song_from_list(song_data)

    def _edit_song_from_list(self, song_data: dict):
        """Открывает песню в редакторе из списка."""
        from ui.main_window import MainWindow
        parent = self.window()
        if isinstance(parent, MainWindow):
            editor_page = parent.get_editor_page()
            if editor_page:
                # Проверяем несохранённые изменения
                if editor_page.song and editor_page._has_unsaved_changes():
                    reply = QMessageBox.question(
                        self, "Несохранённые изменения",
                        "Есть несохранённые изменения. Открыть другую песню?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return

                song = editor.load_song(song_data["id"])
                if song:
                    editor_page.load_existing_song(song)
                    idx = parent._get_page_index("editor")
                    if idx >= 0:
                        parent.stacked.setCurrentIndex(idx)
                        parent.nav_list.setCurrentRow(idx)

    def _delete_song_from_list(self, song_data: dict):
        """Удаляет песню из списка."""
        reply = QMessageBox.question(
            self, "Удаление",
            f"Удалить песню '{song_data['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if editor.delete_song(song_data["id"]):
                QMessageBox.information(self, "Удалено", "Песня удалена!")
                self._refresh_songs()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить песню")

    def _clone_song(self, song_data: dict):
        """Клонирует песню."""
        reply = QMessageBox.question(
            self, "Клонирование",
            f"Создать копию песни '{song_data['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            cloned = editor.clone_song(song_data["id"])
            if cloned:
                QMessageBox.information(
                    self, "Готово",
                    f"Песня клонирована:\n{cloned['title']}"
                )
                self._refresh_songs()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось клонировать песню")

    def _download_txt(self, song_data: dict):
        """Скачивает текст песни в TXT."""
        from PyQt6.QtWidgets import QFileDialog
        from utils.export import export_to_txt

        song = editor.load_song(song_data["id"])
        if not song:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить песню")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить текст",
            f"{song['title']}.txt",
            "Текстовые файлы (*.txt)"
        )

        if output_path:
            try:
                text = export_to_txt(song)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(
                    self, "Готово",
                    f"Текст сохранён в:\n{output_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка",
                    f"Не удалось сохранить:\n{str(e)}"
                )

    def _view_song(self, song_data: dict):
        """Показывает текст песни."""
        song = editor.load_song(song_data["id"])
        if song:
            text = editor.get_song_text(song)
            QMessageBox.information(
                self, f"Песня: {song['title']}",
                text
            )
