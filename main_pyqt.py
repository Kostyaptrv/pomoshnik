import sys
import os

# Fix working directory for frozen apps
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

# Add project root to path - works in both frozen and dev mode
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_dir)

# Ensure PyQt6 is available
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(base_dir, 'PyQt6', 'Qt6', 'plugins') if os.path.exists(os.path.join(base_dir, 'PyQt6', 'Qt6', 'plugins')) else ''

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
