"""Toast-уведомления для PyQt6."""

from PyQt6.QtWidgets import QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont


class Toast(QLabel):
    """Всплывающее уведомление."""

    COLORS = {
        "success": "#4ade80",
        "error": "#ef4444",
        "warning": "#fbbf24",
        "info": "#60a5fa",
    }

    def __init__(self, message: str, level: str = "info", parent=None):
        super().__init__(message, parent)
        self.level = level
        self._init_ui()

    def _init_ui(self):
        self.setFixedHeight(48)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))

        # Рассчитываем ширину на основе текста
        metrics = self.fontMetrics()
        text_width = metrics.horizontalAdvance(self.text()) + 40
        self.setMinimumWidth(max(text_width, 200))
        self.setMaximumWidth(500)

        color = self.COLORS.get(self.level, self.COLORS["info"])
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: #ffffff;
                border-radius: 12px;
                padding: 0 20px;
            }}
        """)

        # Скрываем изначально
        self.setParent(self.parent())
        self.hide()

    def show_toast(self, duration: int = 3000):
        """Показывает уведомление с анимацией."""
        parent = self.parent()
        if not parent:
            return

        # Позиция: правый верхний угол
        x = parent.width() - self.minimumWidth() - 20
        y = 20

        self.move(x, y)
        self.show()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Автоматическое скрытие
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self._timer.start(duration)

    def mousePressEvent(self, event):
        """Клик по тосту закрывает его."""
        if self._timer.isActive():
            self._timer.stop()
        self.hide()
        if self.parent():
            self.parent().deleteLater()


class ToastManager:
    """Менеджер уведомлений."""

    def __init__(self, parent):
        self.parent = parent
        self.toasts = []
        self.max_toasts = 3
        self.y_offset = 20

    def show(self, message: str, level: str = "info", duration: int = 3000):
        """Показывает уведомление."""
        # Удаляем старые если превысили лимит
        while len(self.toasts) >= self.max_toasts:
            old = self.toasts.pop(0)
            old.deleteLater()

        toast = Toast(message, level, self.parent)
        self.toasts.append(toast)

        # Позиционируем
        y = self.y_offset + (len(self.toasts) - 1) * 60
        toast_width = toast.minimumWidth()
        toast.move(self.parent.width() - toast_width - 20, y)

        toast.show_toast(duration)

    def success(self, message: str, duration: int = 3000):
        self.show(message, "success", duration)

    def error(self, message: str, duration: int = 4000):
        self.show(message, "error", duration)

    def warning(self, message: str, duration: int = 3000):
        self.show(message, "warning", duration)

    def info(self, message: str, duration: int = 3000):
        self.show(message, "info", duration)
