import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Инициализируем логирование
from utils import logger  # noqa: E402

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow

if __name__ == "__main__":
    logger.logger.info("Приложение запускается")

    app = QApplication(sys.argv)
    app.setApplicationName("Помощник для написания песен")
    app.setOrganizationName("Pomoshnik")

    # Устанавливаем иконку
    icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        logger.logger.info("Иконка приложения установлена")

    window = MainWindow()
    window.show()
    logger.logger.info("Главное окно показано")
    sys.exit(app.exec())
