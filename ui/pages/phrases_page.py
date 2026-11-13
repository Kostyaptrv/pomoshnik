"""Страница библиотеки фраз и метафор."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QTabWidget, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from engine import phrases as phrases_engine


class PhraseCard(QFrame):
    """Карточка фразы."""

    def __init__(self, phrase: str, category: str, parent=None):
        super().__init__(parent)
        self.phrase = phrase
        self._init_ui(category)

    def _init_ui(self, category: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Категория
        cat_label = QLabel(category.upper())
        cat_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        cat_label.setStyleSheet("color: #e94560;")
        layout.addWidget(cat_label)

        # Текст фразы
        text_label = QLabel(self.phrase)
        text_label.setFont(QFont("Segoe UI", 11))
        text_label.setStyleSheet("color: #ffffff; line-height: 1.5;")
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        # Кнопка копирования
        copy_btn = QPushButton("📋 Копировать")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self._copy_phrase)
        layout.addWidget(copy_btn)

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

    def _copy_phrase(self):
        """Копирует фразу в буфер обмена."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.phrase)


class PhrasesPage(QWidget):
    """Страница библиотеки фраз и метафор."""

    def __init__(self, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("📚 Библиотека фраз")
        title.setObjectName("heading_label")
        layout.addWidget(title)

        subtitle = QLabel("Организованные по категориям фразы и метафоры для ваших песен")
        subtitle.setObjectName("subheading_label")
        layout.addWidget(subtitle)

        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск фразы...")
        self.search_input.setFont(QFont("Segoe UI", 11))
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("Найти")
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.clicked.connect(self._search_phrases)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # Табы: категории / поиск / случайные
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладка 1: Категории
        categories_tab = self._create_categories_tab()
        self.tabs.addTab(categories_tab, "📂 Категории")

        # Вкладка 2: Поиск
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        self.search_results = QListWidget()
        self.search_results.itemDoubleClicked.connect(self._on_phrase_selected)
        search_layout.addWidget(self.search_results)
        self.tabs.addTab(search_tab, "🔍 Поиск")

        # Вкладка 3: Случайные
        random_tab = self._create_random_tab()
        self.tabs.addTab(random_tab, "🎲 Случайные")

    def _create_categories_tab(self) -> QWidget:
        """Создаёт вкладку с категориями."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        categories = {
            "love": ("❤️", "Любовь"),
            "nature": ("🌿", "Природа"),
            "pain": ("💔", "Боль"),
            "hope": ("🌟", "Надежда"),
            "dreams": ("💭", "Мечты"),
            "time": ("⏰", "Время"),
        }

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.categories_layout = QVBoxLayout(scroll_content)
        self.categories_layout.setSpacing(12)

        for cat_key, (icon, cat_name) in categories.items():
            phrases = phrases_engine.get_phrases_by_category(cat_key)
            card = self._create_category_card(icon, cat_name, phrases, cat_key)
            self.categories_layout.addWidget(card)

        self.categories_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Кнопка создания категории
        add_cat_btn = QPushButton("➕ Создать категорию")
        add_cat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_cat_btn.clicked.connect(self._create_category_dialog)
        layout.addWidget(add_cat_btn)

        return widget

    def _create_category_card(self, icon: str, name: str, phrases: list, category: str) -> QFrame:
        """Создаёт карточку категории."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #e94560;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # Заголовок
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        header_layout.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(name_label)

        count_label = QLabel(f"({len(phrases)} фраз)")
        count_label.setFont(QFont("Segoe UI", 10))
        count_label.setStyleSheet("color: #6c6c8a;")
        header_layout.addWidget(count_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Примеры фраз
        examples = phrases[:3]
        for phrase in examples:
            phrase_label = QLabel(f"• {phrase}")
            phrase_label.setFont(QFont("Segoe UI", 10))
            phrase_label.setStyleSheet("color: #b8b8d4;")
            phrase_label.setWordWrap(True)
            layout.addWidget(phrase_label)

        if len(phrases) > 3:
            more_label = QLabel(f"...и ещё {len(phrases) - 3}")
            more_label.setFont(QFont("Segoe UI", 9))
            more_label.setStyleSheet("color: #6c6c8a;")
            layout.addWidget(more_label)

        layout.addStretch()
        return card

    def _create_random_tab(self) -> QWidget:
        """Создаёт вкладку случайных фраз."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # Кнопка генерации
        gen_btn = QPushButton("🎲 Сгенерировать случайные фразы")
        gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_btn.clicked.connect(self._generate_random)
        layout.addWidget(gen_btn)

        self.random_list = QListWidget()
        self.random_list.itemDoubleClicked.connect(self._on_phrase_selected)
        layout.addWidget(self.random_list)

        # Фильтр по категории
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр по категории:"))
        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText("love, nature, pain...")
        filter_layout.addWidget(self.category_filter)
        layout.addLayout(filter_layout)

        return widget

    def _search_phrases(self):
        """Поиск фраз по ключевому слову."""
        keyword = self.search_input.text().strip()
        if not keyword:
            self.search_results.clear()
            self.search_results.addItem("Введите слово для поиска")
            return

        results = phrases_engine.search_phrases(keyword)
        self.search_results.clear()

        if results:
            for result in results:
                item = QListWidgetItem(f"📝 {result['phrase']}")
                item.setData(Qt.ItemDataRole.UserRole, result)
                self.search_results.addItem(item)
        else:
            self.search_results.addItem(f"😔 Фразы с ключевым словом '{keyword}' не найдены")

    def _generate_random(self):
        """Генерирует случайные фразы."""
        category = self.category_filter.text().strip() or None
        count = 5

        random_phrases = phrases_engine.get_random_phrases(count=count, category=category)
        self.random_list.clear()

        if random_phrases:
            for phrase in random_phrases:
                item = QListWidgetItem(f"💭 {phrase}")
                item.setData(Qt.ItemDataRole.UserRole, {"phrase": phrase, "category": category or "all"})
                self.random_list.addItem(item)
        else:
            self.random_list.addItem("😔 Не удалось сгенерировать фразы")

    def _on_phrase_selected(self, item: QListWidgetItem):
        """Обработка выбора фразы."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, dict) and "phrase" in data:
            # Копируем в буфер
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(data["phrase"])

            # Показываем уведомление
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Скопировано",
                f"Фраза скопирована:\n\n{data['phrase']}"
            )

    def _create_category_dialog(self):
        """Открывает диалог создания новой категории."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Новая категория")
        dialog.setMinimumSize(400, 200)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Название новой категории:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("например: осень, город, свобода...")
        layout.addWidget(name_input)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Создать")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(lambda: self._save_category(name_input.text(), dialog))
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.exec()

    def _save_category(self, name: str, dialog):
        """Сохраняет новую категорию."""
        if not name.strip():
            QMessageBox.warning(self, "Ошибка", "Введите название категории")
            return

        category = name.strip().lower()
        if phrases_engine.create_custom_category(category):
            self._refresh_categories()
            QMessageBox.information(self, "Готово", f"Категория '{name}' создана!")
        else:
            QMessageBox.warning(self, "Ошибка", f"Категория '{name}' уже существует")
        dialog.accept()

    def _refresh_categories(self):
        """Обновляет список категорий."""
        from engine import phrases as phrases_engine

        categories = {
            "love": ("❤️", "Любовь"),
            "nature": ("🌿", "Природа"),
            "pain": ("💔", "Боль"),
            "hope": ("🌟", "Надежда"),
            "dreams": ("💭", "Мечты"),
            "time": ("⏰", "Время"),
        }

        # Очищаем
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Загружаем все категории
        all_cats = phrases_engine.get_all_categories()

        for cat_key in all_cats:
            icon = categories.get(cat_key, "📝")
            cat_name = categories.get(cat_key, ("📝", cat_key.capitalize()))[1]
            phrases = phrases_engine.get_phrases_by_category(cat_key)

            card = self._create_category_card(icon, cat_name, phrases, cat_key)
            self.categories_layout.addWidget(card)

        self.categories_layout.addStretch()

    def _add_phrase_to_category(self, category: str):
        """Открывает диалог добавления фразы в категорию."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Добавить фразу в '{category}'")
        dialog.setMinimumSize(400, 250)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Текст фразы:"))
        phrase_input = QLineEdit()
        phrase_input.setPlaceholderText("Введите фразу...")
        layout.addWidget(phrase_input)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Добавить")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(lambda: self._save_phrase(category, phrase_input.text(), dialog))
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.exec()

    def _save_phrase(self, category: str, phrase: str, dialog):
        """Сохраняет фразу в категорию."""
        if not phrase.strip():
            QMessageBox.warning(self, "Ошибка", "Введите текст фразы")
            return

        if phrases_engine.add_custom_phrase(category, phrase.strip()):
            QMessageBox.information(self, "Готово", "Фраза добавлена!")
            self._refresh_categories()
        else:
            QMessageBox.warning(self, "Ошибка", "Такая фраза уже существует")
        dialog.accept()
