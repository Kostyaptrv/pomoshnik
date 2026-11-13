"""Загрузочный спиннер для долгих операций."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class LoadingOverlay(QWidget):
    """Оверлей загрузки поверх виджета."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._hide()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 52, 96, 230);
                border-radius: 12px;
            }
        """)
        self.setFixedHeight(150)
        self.setFixedWidth(300)

        # Текст загрузки
        self.label = QLabel("Загрузка...")
        self.label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #ffffff;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Прогресс-бар
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1f2b4d;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e94560, stop:1 #0f3460);
                border-radius: 4px;
            }
        """)
        self.progress.setRange(0, 0)  # Бесконечный прогресс
        layout.addWidget(self.progress)

    def show_loading(self, text: str = "Загрузка..."):
        """Показывает оверлей загрузки."""
        self.label.setText(text)
        self._show()

    def hide_loading(self):
        """Скрывает оверлей загрузки."""
        self._hide()

    def _show(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()

    def _hide(self):
        self.hide()
