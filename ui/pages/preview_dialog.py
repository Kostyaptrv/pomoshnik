"""Предпросмотр песни в отдельном окне."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QPushButton, QFrame, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PreviewDialog(QDialog):
    """Окно предпросмотра текста песни."""

    def __init__(self, song, parent=None):
        super().__init__(parent)
        self.song = song
        self.setWindowTitle(f"Предпросмотр: {song.get('title', 'Песня')}")
        self.setMinimumSize(700, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel(song.get('title', 'Без названия'))
        title.setObjectName('heading_label')
        layout.addWidget(title)

        # Метаданные
        meta_layout = QHBoxLayout()
        style = song.get('style_id', 'N/A')
        created = song.get('created_at', '')[:10] if song.get('created_at') else 'N/A'
        meta_layout.addWidget(QLabel(f"🎵 Стиль: {style}"))
        meta_layout.addWidget(QLabel(f"📅 Создано: {created}"))
        meta_layout.addStretch()
        layout.addLayout(meta_layout)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #2a2a4a;")
        layout.addWidget(line)

        # Секции
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        text_layout = QVBoxLayout(content)
        text_layout.setSpacing(12)

        sections = song.get('sections', {})
        for section_key, section_data in sections.items():
            label = section_data.get('label', section_key)
            text = section_data.get('text', '').strip()
            section_type = section_data.get('type', 'unknown')

            # Карточка секции
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #16213e;
                    border: 1px solid #2a2a4a;
                    border-radius: 10px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(6)

            # Заголовок секции
            type_icons = {
                'куплет': '🎤', 'припев': '🔊', 'бридж': '🌉',
                'интро': '🎬', 'проигрыш': '🎸', 'аутро': '🏁'
            }
            icon = type_icons.get(section_type, '🎵')
            section_header = QLabel(f"{icon} {label} ({section_type})")
            section_header.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
            section_header.setStyleSheet('color: #e94560;')
            card_layout.addWidget(section_header)

            # Текст секции
            if text:
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        line_label = QLabel(f'  • {line}')
                        line_label.setFont(QFont('Segoe UI', 10))
                        line_label.setStyleSheet('color: #ffffff;')
                        line_label.setWordWrap(True)
                        line_label.setFixedHeight(22)
                        card_layout.addWidget(line_label)
            else:
                empty_label = QLabel('  (пусто)')
                empty_label.setFont(QFont('Segoe UI', 10))
                empty_label.setStyleSheet('color: #6c6c8a; font-style: italic;')
                card_layout.addWidget(empty_label)

            text_layout.addWidget(card)

        text_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # Кнопки
        btn_layout = QHBoxLayout()
        close_btn = QPushButton('Закрыть')
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
