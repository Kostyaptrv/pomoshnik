"""Главное окно приложения."""

import os
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont

from ui.pages.home_page import HomePage
from ui.pages.rhymes_page import RhymesPage
from ui.pages.templates_page import TemplatesPage
from ui.pages.editor_page import EditorPage
from ui.pages.songs_page import SongsPage
from ui.pages.phrases_page import PhrasesPage


class MainWindow(QMainWindow):
    """Главное окно с боковой панелью и страницами."""

    PAGES = [
        ("🏠 Главная", "home", HomePage),
        ("🔤 Рифмы", "rhymes", RhymesPage),
        ("📋 Шаблоны", "templates", TemplatesPage),
        ("✍️ Редактор", "editor", EditorPage),
        ("📚 Фразы", "phrases", PhrasesPage),
        ("🎶 Мои песни", "songs", SongsPage),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Помощник для написания песен")
        self.setMinimumSize(1200, 800)
        self.is_dark_theme = True

        self._load_stylesheet()

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)

        self.stacked = QStackedWidget()
        content_layout.addWidget(self.stacked)

        main_layout.addWidget(content_widget, 1)

        self._add_pages()
        self._load_state()
        self._navigate_to_index(0)

        # Менеджер уведомлений
        from ui.components.toast import ToastManager
        self.toast_manager = ToastManager(self)

        # Проверка обновлений (через 2 секунды после запуска)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self._check_for_updates)

    def _load_stylesheet(self):
        """Загружает QSS тему."""
        theme = "dark_theme.qss" if self.is_dark_theme else "light_theme.qss"
        
        # Get base path - works in both frozen and dev mode
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        
        qss_path = os.path.join(base_dir, "assets", "qss", theme)
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _toggle_theme(self):
        """Переключает тему."""
        self.is_dark_theme = not self.is_dark_theme
        self.theme_btn.setText("🌙 Тёмная тема" if self.is_dark_theme else "🌞 Светлая тема")
        self._load_stylesheet()
        self._save_state()

    def _load_state(self):
        """Загружает состояние приложения."""
        import sys
        state_path = os.path.join(
            os.path.dirname(sys.executable),
            "data", "app_state.json"
        )
        if os.path.exists(state_path):
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    import json
                    state = json.load(f)

                # Восстанавливаем тему
                if "is_dark_theme" in state:
                    self.is_dark_theme = state["is_dark_theme"]
                    self.theme_btn.setText("🌙 Тёмная тема" if self.is_dark_theme else "🌞 Светлая тема")

                # Восстанавливаем последнюю страницу
                last_page = state.get("last_page", "home")
                idx = self._get_page_index(last_page)
                if idx >= 0:
                    self._navigate_to_index(idx)
            except Exception:
                pass

    def _save_state(self):
        """Сохраняет состояние приложения."""
        import sys
        state_path = os.path.join(
            os.path.dirname(sys.executable),
            "data", "app_state.json"
        )
        try:
            import json
            current_idx = self.stacked.currentIndex()
            current_key = self.nav_list.item(current_idx).data(Qt.ItemDataRole.UserRole)

            state = {
                "last_page": current_key,
                "is_dark_theme": self.is_dark_theme
            }
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _create_sidebar(self) -> QWidget:
        """Создаёт боковую панель навигации."""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(6)

        # Логотип
        logo = QLabel("🎵 Помощник")
        logo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("""
            background-color: #16213e;
            border: 1px solid #2a2a4a;
            border-radius: 12px;
            padding: 8px;
        """)
        logo.setFixedHeight(50)
        layout.addWidget(logo)

        # Навигация
        self.nav_items = [
            ("🏠 Главная", "home"),
            ("🔤 Рифмы", "rhymes"),
            ("📋 Шаблоны", "templates"),
            ("✍️ Редактор", "editor"),
            ("📚 Фразы", "phrases"),
            ("🎶 Мои песни", "songs"),
        ]

        self.nav_list = QListWidget()
        for label, key in self.nav_items:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.nav_list.addItem(item)

        self.nav_list.setCurrentRow(0)
        self.nav_list.itemClicked.connect(self._on_nav_clicked)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #1f2b4d;
            }
            QListWidget::item:selected {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e94560, stop:1 #0f3460);
                color: #ffffff;
            }
        """)
        layout.addWidget(self.nav_list)

        # Кнопка переключения темы
        self.theme_btn = QPushButton("🌙 Тёмная тема")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1f2b4d;
                border-color: #e94560;
            }
        """)
        layout.addWidget(self.theme_btn)

        # Разделитель
        layout.addStretch()

        return sidebar

    def _add_pages(self):
        """Добавляет все страницы в stacked widget."""
        for _, key, page_class in self.PAGES:
            if page_class is None:
                placeholder = QLabel(f"\U0001f6a8 Страница в разработке")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                placeholder.setObjectName("subheading_label")
                placeholder.setMinimumHeight(300)
                self.stacked.addWidget(placeholder)
            else:
                page = page_class(key, self)
                self.stacked.addWidget(page)
                if key == "editor":
                    self.editor_page = page
                elif key == "rhymes":
                    self.rhymes_page = page

    def _navigate_to_index(self, index: int):
        """Переходит к странице по индексу с анимацией."""
        # Анимация перехода
        current_widget = self.stacked.currentWidget()
        if current_widget and self.stacked.currentIndex() != index:
            # Скрываем текущую страницу
            current_widget.setWindowOpacity(0)
            self._fade_out(current_widget)

        self.stacked.setCurrentIndex(index)
        new_widget = self.stacked.currentWidget()
        if new_widget:
            new_widget.setWindowOpacity(0)
            self._fade_in(new_widget)

        self._save_state()

    def _fade_out(self, widget: QWidget):
        """Плавное исчезновение виджета."""
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(200)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()

    def _fade_in(self, widget: QWidget):
        """Плавное появление виджета."""
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()

    def _check_for_updates(self):
        """Проверяет наличие обновлений."""
        from ui.components.update_dialog import UpdateDialog
        
        try:
            dialog = UpdateDialog(self)
            dialog.exec()
        except Exception as e:
            # Не критично — если проверка не удалась, просто продолжаем
            pass

    def _on_nav_clicked(self, item: QListWidgetItem):
        """Обработчик клика по пункту навигации."""
        key = item.data(Qt.ItemDataRole.UserRole)
        idx = self._get_page_index(key)
        if idx >= 0:
            self._navigate_to_index(idx)

    def _get_page_index(self, key: str) -> int:
        """Возвращает индекс страницы по key."""
        for i, (_, k, _) in enumerate(self.PAGES):
            if k == key:
                return i
        return -1

    def get_editor_page(self) -> EditorPage:
        """Возвращает страницу редактора."""
        return self.editor_page

    def closeEvent(self, event):
        """Сохраняет состояние при закрытии."""
        self._save_state()
        event.accept()
