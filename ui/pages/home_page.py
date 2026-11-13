"""Главная страница приложения."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from engine import rhymes
from engine import editor
from engine import structure


class HomePage(QWidget):
    """Главная страница с карточками функций и статистикой."""

    def __init__(self, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Помощник для написания песен")
        title.setObjectName("title_label")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            "Создавайте музыку вместе с AI — рифмы, шаблоны, редактор"
        )
        subtitle.setObjectName("subheading_label")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Feature cards
        heading = QLabel("✨ Возможности")
        heading.setObjectName("heading_label")
        layout.addWidget(heading)

        self._create_feature_cards(layout)

        # Popular words
        self._create_popular_words(layout)

        # Stats
        self._create_stats(layout)

        layout.addStretch()

    def _create_feature_cards(self, parent_layout):
        """Создаёт карточки возможностей."""
        features = [
            ("🔤", "Поиск рифм", "Находите рифмы к любому слову по окончанию или точно", "rhymes"),
            ("📋", "Шаблоны песен", "Выбирайте готовые структуры для разных жанров", "templates"),
            ("✍️", "Редактор", "Пишите текст песен с подсказками и советами", "editor"),
        ]

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        for icon, title_text, desc, key in features:
            card = QFrame()
            card.setObjectName("card_frame")
            card.setFixedHeight(180)
            card.setCursor(Qt.CursorShape.PointingHandCursor)

            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.setSpacing(8)

            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 36))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_label)

            title_l = QLabel(title_text)
            title_l.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            title_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_l.setStyleSheet("color: #ffffff;")
            card_layout.addWidget(title_l)

            desc_l = QLabel(desc)
            desc_l.setObjectName("subheading_label")
            desc_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_l.setWordWrap(True)
            card_layout.addWidget(desc_l)

            card.mousePressEvent = lambda e, k=key: self._navigate_to(k)  # noqa

            cards_layout.addWidget(card, 1)

        parent_layout.addLayout(cards_layout)

    def _create_popular_words(self, parent_layout):
        """Создаёт секцию популярных слов в виде выровненной сетки."""
        heading = QLabel("🔥 Популярные слова")
        heading.setObjectName("heading_label")
        parent_layout.addWidget(heading)

        popular = rhymes.get_common_rhymes()
        cols = 5

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rows = (len(popular) + cols - 1) // cols
        for row in range(rows):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(8)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Каждая строка имеет ровно cols кнопок (одинаковая ширина)
            count_in_row = min(cols, len(popular) - row * cols)
            stretch_before = (cols - count_in_row) // 2

            for s in range(stretch_before):
                row_layout.addStretch()

            for col in range(count_in_row):
                idx = row * cols + col
                word = popular[idx]
                btn = QPushButton(f"🎯 {word.capitalize()}")
                btn.setObjectName("small_button")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setMinimumHeight(36)
                btn.setFixedWidth(140)
                btn.clicked.connect(lambda checked, w=word: self._navigate_to("rhymes", w))
                row_layout.addWidget(btn)

            for s in range(cols - count_in_row - stretch_before):
                row_layout.addStretch()

            layout.addLayout(row_layout)

        parent_layout.addWidget(container)

    def _create_stats(self, parent_layout):
        """Создаёт карточки статистики."""
        all_songs = editor.get_all_songs()
        total_songs = len(all_songs)
        styles_count = len(structure.get_available_styles())
        popular = rhymes.get_common_rhymes()

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        for value, label in [
            (str(total_songs), "Песен создано"),
            (str(styles_count), "Жанров"),
            (str(len(popular)), "Слов в словаре"),
        ]:
            card = QFrame()
            card.setObjectName("card_frame")
            card.setFixedWidth(200)

            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.setSpacing(4)

            val_label = QLabel(value)
            val_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
            val_label.setStyleSheet("color: #e94560;")
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(val_label)

            lbl = QLabel(label)
            lbl.setObjectName("subheading_label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(lbl)

            stats_layout.addWidget(card, 1)

        parent_layout.addLayout(stats_layout)

    def _navigate_to(self, page_key: str, word: str = None):
        """Переход на другую страницу."""
        from ui.main_window import MainWindow
        parent = self.window()
        if isinstance(parent, MainWindow):
            idx = parent._get_page_index(page_key)
            if idx >= 0:
                parent.stacked.setCurrentIndex(idx)
                parent.nav_list.setCurrentRow(idx)

                # Если есть слово для поиска и это страница рифм
                if word and page_key == 'rhymes':
                    rhymes_page = parent.rhymes_page if hasattr(parent, 'rhymes_page') else None
                    if rhymes_page:
                        rhymes_page.set_search_word(word)

    def _set_search_word(self, word: str):
        """Устанавливает слово для поиска (вызывается при переходе)."""
        if hasattr(self, '_navigate_to'):
            self._navigate_to('rhymes', word)
