"""Страница выбора шаблонов песен."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QFont

from engine import structure


class TemplatesPage(QWidget):
    """Страница выбора жанра/шаблона."""

    template_selected = Signal(str)

    def __init__(self, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Заголовок
        title = QLabel("📋 Шаблоны песен")
        title.setObjectName("heading_label")
        layout.addWidget(title)

        subtitle = QLabel("Выберите жанр для создания песни")
        subtitle.setObjectName("subheading_label")
        layout.addWidget(subtitle)

        # Сетка карточек
        self._create_template_cards(layout)

    def _create_template_cards(self, parent_layout):
        """Создаёт карточки шаблонов жанров."""
        styles = structure.get_available_styles()
        icons = {
            "поп": "🎤", "рок": "🎸", "рэп": "🎙️",
            "баллада": "🎻", "инди": "🌿", "шансон": "🎩",
        }

        num_cols = 3
        for i in range(0, len(styles), num_cols):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(16)

            batch = styles[i:i + num_cols]
            for style in batch:
                card = self._create_template_card(style, icons.get(style["id"], "🎵"))
                row_layout.addWidget(card, 1)

            parent_layout.addLayout(row_layout)

    def _create_template_card(self, style: dict, icon: str) -> QFrame:
        """Создаёт карточку шаблона."""
        card = QFrame()
        card.setObjectName("card_frame")
        card.setFixedHeight(160)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 12)

        # Иконка
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 32))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Название
        name_label = QLabel(style["name"])
        name_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #ffffff;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Описание
        desc_label = QLabel(style["description"])
        desc_label.setObjectName("subheading_label")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        layout.addStretch()

        # Кнопка
        btn = QPushButton(f"Выбрать {style['name']}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda checked, sid=style["id"]: self._select_template(sid))
        layout.addWidget(btn)

        return card

    def _select_template(self, style_id: str):
        """Выбирает шаблон и переходит к редактору."""
        try:
            from ui.main_window import MainWindow
            parent = self.window()
            if isinstance(parent, MainWindow):
                idx = parent._get_page_index("editor")
                if idx >= 0:
                    parent.stacked.setCurrentIndex(idx)
                    parent.nav_list.setCurrentRow(parent._get_page_index("editor"))

                    # Передаём selected template на editor page
                    if hasattr(parent, 'editor_page'):
                        parent.editor_page.set_template(style_id)
            self.template_selected.emit(style_id)
        except Exception as e:
            import traceback
            print(f"ERROR in _select_template: {e}")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось выбрать шаблон:\n{e}\n\n{traceback.format_exc()}"
            )
