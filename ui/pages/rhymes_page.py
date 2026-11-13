"""Страница поиска рифм."""

import os
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QTabWidget, QSlider, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal

from engine import rhymes


class RhymesPage(QWidget):
    """Страница поиска рифм с тремя вкладками."""

    search_word_changed = Signal(str)

    def __init__(self, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Заголовок
        title = QLabel("🔤 Поиск рифм")
        title.setObjectName("heading_label")
        layout.addWidget(title)

        subtitle = QLabel("Введите слово или окончание для поиска рифм")
        subtitle.setObjectName("subheading_label")
        layout.addWidget(subtitle)

        # Табы
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладка 1: По слову
        tab1 = self._create_word_tab()
        self.tabs.addTab(tab1, "🔍 По слову")

        # Вкладка 2: По окончанию
        tab2 = self._create_ending_tab()
        self.tabs.addTab(tab2, "✨ По окончанию")

        # Вкладка 3: Популярные
        tab3 = self._create_popular_tab()
        self.tabs.addTab(tab3, "📊 Популярные")

        # Вкладка 4: Избранное
        tab4 = self._create_favorites_tab()
        self.tabs.addTab(tab4, "⭐ Избранное")

        # Вкладка 5: История
        tab5 = self._create_history_tab()
        self.tabs.addTab(tab5, "📜 История")

    def _create_word_tab(self) -> QWidget:
        """Вкладка поиска по слову."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # Поиск
        search_layout = QHBoxLayout()
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("например: любовь, свет, ночь...")
        search_layout.addWidget(self.word_input)

        self.word_max = QSlider(Qt.Orientation.Horizontal)
        self.word_max.setMinimum(5)
        self.word_max.setMaximum(50)
        self.word_max.setValue(10)
        self.word_max.setFixedWidth(150)
        self.word_max_label = QLabel("10")
        self.word_max.valueChanged.connect(lambda v: self.word_max_label.setText(str(v)))
        search_layout.addWidget(self.word_max)
        search_layout.addWidget(self.word_max_label)
        layout.addLayout(search_layout)

        # Кнопка
        search_btn = QPushButton("🔎 Найти рифмы")
        search_btn.clicked.connect(self._search_by_word)
        layout.addWidget(search_btn)

        # Результаты
        self.word_results = QListWidget()
        self.word_results.itemDoubleClicked.connect(self._on_rhyme_clicked)
        layout.addWidget(self.word_results)

        # Кнопка добавления в избранное
        self.add_favorite_btn = QPushButton("⭐ В избранное")
        self.add_favorite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_favorite_btn.clicked.connect(self._add_current_word_to_favorites)
        layout.addWidget(self.add_favorite_btn)
        self.add_favorite_btn.setVisible(False)

        return widget

    def _create_ending_tab(self) -> QWidget:
        """Вкладка поиска по окончанию."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # Поиск
        ending_layout = QHBoxLayout()
        self.ending_input = QLineEdit()
        self.ending_input.setPlaceholderText("-ция, -сть, -ть...")
        ending_layout.addWidget(self.ending_input)

        self.ending_min = QSlider(Qt.Orientation.Horizontal)
        self.ending_min.setMinimum(1)
        self.ending_min.setMaximum(10)
        self.ending_min.setValue(2)
        self.ending_min_label = QLabel("2")
        self.ending_min.valueChanged.connect(lambda v: self.ending_min_label.setText(str(v)))
        ending_layout.addWidget(self.ending_min)
        ending_layout.addWidget(self.ending_min_label)
        layout.addLayout(ending_layout)

        max_layout = QHBoxLayout()
        self.ending_max = QSlider(Qt.Orientation.Horizontal)
        self.ending_max.setMinimum(5)
        self.ending_max.setMaximum(50)
        self.ending_max.setValue(15)
        self.ending_max_label = QLabel("15")
        self.ending_max.valueChanged.connect(lambda v: self.ending_max_label.setText(str(v)))
        max_layout.addWidget(QLabel("Максимум:"))
        max_layout.addWidget(self.ending_max)
        max_layout.addWidget(self.ending_max_label)
        layout.addLayout(max_layout)

        # Кнопка
        search_btn = QPushButton("🔎 Найти по окончанию")
        search_btn.clicked.connect(self._search_by_ending)
        layout.addWidget(search_btn)

        # Результаты
        self.ending_results = QListWidget()
        self.ending_results.itemDoubleClicked.connect(self._on_rhyme_clicked)
        layout.addWidget(self.ending_results)

        return widget

    def _create_popular_tab(self) -> QWidget:
        """Вкладка популярных слов."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        subtitle = QLabel("Самые популярные слова для рифмовки")
        subtitle.setObjectName("subheading_label")
        layout.addWidget(subtitle)

        self.popular_list = QListWidget()
        self._load_popular_words()
        self.popular_list.itemDoubleClicked.connect(self._on_rhyme_clicked)
        layout.addWidget(self.popular_list)

        return widget

    def _create_favorites_tab(self) -> QWidget:
        """Вкладка избранных рифм."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        subtitle = QLabel("Ваши сохранённые рифмы")
        subtitle.setObjectName("subheading_label")
        layout.addWidget(subtitle)

        self.favorites_list = QListWidget()
        self._load_favorites()
        self.favorites_list.itemDoubleClicked.connect(self._on_favorite_clicked)
        layout.addWidget(self.favorites_list)

        # Кнопка удаления
        clear_btn = QPushButton("🗑 Очистить избранное")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_favorites)
        layout.addWidget(clear_btn)

        return widget

    def _create_history_tab(self) -> QWidget:
        """Вкладка истории поиска."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        subtitle = QLabel("Последние поисковые запросы")
        subtitle.setObjectName("subheading_label")
        layout.addWidget(subtitle)

        self.history_list = QListWidget()
        self._load_history()
        self.history_list.itemDoubleClicked.connect(self._on_history_clicked)
        layout.addWidget(self.history_list)

        # Кнопка очистки
        clear_btn = QPushButton("🗑 Очистить историю")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)

        return widget

    def _load_popular_words(self):
        """Загружает популярные слова."""
        self.popular_list.clear()
        popular = rhymes.get_common_rhymes()
        for word in popular:
            rhyme_count = len(rhymes.get_rhymes(word))
            item = QListWidgetItem(f"{word.capitalize()} ({rhyme_count} рифм)")
            item.setData(Qt.ItemDataRole.UserRole, word.lower())
            self.popular_list.addItem(item)

    def _search_by_word(self):
        """Поиск рифм по слову."""
        word = self.word_input.text().strip()
        if not word:
            self.add_favorite_btn.setVisible(False)
            return

        # Сохраняем в историю
        self._save_search_history(word)

        max_res = self.word_max.value()
        result = rhymes.get_rhymes(word, max_results=max_res)

        self.word_results.clear()
        if result:
            for rhyme in result:
                item = QListWidgetItem(f"💡 {rhyme.capitalize()}")
                item.setData(Qt.ItemDataRole.UserRole, rhyme.lower())
                self.word_results.addItem(item)
            # Показываем кнопку добавления в избранное
            self.add_favorite_btn.setVisible(True)
        else:
            self.word_results.addItem(f"😔 Рифмы к слову «{word}» не найдены")
            self.add_favorite_btn.setVisible(False)

    def _search_by_ending(self):
        """Поиск по окончанию."""
        ending = self.ending_input.text().strip()
        if not ending:
            return

        min_len = self.ending_min.value()
        max_res = self.ending_max.value()
        result = rhymes.get_rhymes_by_ending(ending, min_length=min_len, max_results=max_res)

        self.ending_results.clear()
        if result:
            for word in result:
                item = QListWidgetItem(f"📝 {word.capitalize()}")
                item.setData(Qt.ItemDataRole.UserRole, word.lower())
                self.ending_results.addItem(item)
        else:
            self.ending_results.addItem(f"😔 Слова с окончанием «{ending}» не найдены")

    def _on_rhyme_clicked(self, item: QListWidgetItem):
        """Обработка клика по рифме — переход к поиску."""
        word = item.data(Qt.ItemDataRole.UserRole)
        if word:
            self.word_input.setText(word)
            self._search_by_word()
            # Переключаемся на вкладку "По слову"
            self.tabs.setCurrentIndex(0)

    def _on_history_clicked(self, item: QListWidgetItem):
        """Обработка клика по истории поиска."""
        word = item.data(Qt.ItemDataRole.UserRole)
        if word:
            self.word_input.setText(word)
            self._search_by_word()
            self.tabs.setCurrentIndex(0)

    def _save_search_history(self, word: str):
        """Сохраняет запрос в историю."""
        history_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "search_history.json"
        )
        try:
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            else:
                history = []

            # Удаляем дубликаты
            history = [h for h in history if h.lower() != word.lower()]
            # Добавляем в начало
            history.insert(0, word)
            # Ограничиваем 50 записями
            history = history[:50]

            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(history, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_history(self):
        """Загружает историю поиска."""
        self.history_list.clear()
        try:
            history_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "search_history.json"
            )
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
                for word in history:
                    item = QListWidgetItem(f"🔍 {word.capitalize()}")
                    item.setData(Qt.ItemDataRole.UserRole, word.lower())
                    self.history_list.addItem(item)
        except Exception:
            pass

    def _clear_history(self):
        """Очищает историю поиска."""
        reply = QMessageBox.question(
            self, "Очистка",
            "Удалить всю историю поиска?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            history_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "search_history.json"
            )
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            self._load_history()
            QMessageBox.information(self, "Готово", "История очищена")

    def _on_favorite_clicked(self, item: QListWidgetItem):
        """Обработка клика по избранной рифме."""
        word = item.data(Qt.ItemDataRole.UserRole)
        if word:
            self.word_input.setText(word)
            self._search_by_word()
            self.tabs.setCurrentIndex(0)

    def _load_favorites(self):
        """Загружает избранные рифмы."""
        self.favorites_list.clear()
        try:
            fav_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "favorites.json"
            )
            if os.path.exists(fav_path):
                with open(fav_path, "r", encoding="utf-8") as f:
                    favorites = json.load(f)
                for word in favorites:
                    item = QListWidgetItem(f"⭐ {word.capitalize()}")
                    item.setData(Qt.ItemDataRole.UserRole, word.lower())
                    self.favorites_list.addItem(item)
        except Exception:
            pass

    def _save_favorite(self, word: str):
        """Сохраняет рифму в избранное."""
        fav_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "favorites.json"
        )
        try:
            if os.path.exists(fav_path):
                with open(fav_path, "r", encoding="utf-8") as f:
                    favorites = json.load(f)
            else:
                favorites = {}

            if word.lower() not in favorites:
                favorites[word.lower()] = True
                with open(fav_path, "w", encoding="utf-8") as f:
                    json.dump(favorites, ensure_ascii=False, indent=2)
                self._load_favorites()
                QMessageBox.information(self, "Сохранено", f"'{word}' добавлено в избранное")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {str(e)}")

    def _clear_favorites(self):
        """Очищает избранное."""
        reply = QMessageBox.question(
            self, "Очистка",
            "Удалить все избранные рифмы?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            fav_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "favorites.json"
            )
            with open(fav_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            self._load_favorites()
            QMessageBox.information(self, "Готово", "Избранное очищено")

    def _add_current_word_to_favorites(self):
        """Добавляет текущее слово поиска в избранное."""
        word = self.word_input.text().strip()
        if word:
            self._save_favorite(word)

    def set_search_word(self, word: str):
        """Устанавливает слово для поиска."""
        self.word_input.setText(word)
        self._search_by_word()
