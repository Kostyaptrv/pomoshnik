"""Диалог проверки и установки обновлений."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from utils.updater import (
    check_for_updates,
    download_update,
    cleanup_update,
    format_size,
    format_date,
    APP_VERSION
)


class UpdateCheckThread(QThread):
    """Фоновый поток для проверки обновлений."""
    
    finished = pyqtSignal(object)  # dict или None
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            result = check_for_updates()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class DownloadUpdateThread(QThread):
    """Фоновый поток для скачивания обновления."""
    
    finished = pyqtSignal(str)  # путь к файлу
    progress = pyqtSignal(int, int)  # current, total
    error = pyqtSignal(str)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            def progress_callback(current, total):
                self.progress.emit(current, total)
            
            result = download_update(self.url, progress_callback)
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("Не удалось скачать обновление")
        except Exception as e:
            self.error.emit(f"Ошибка скачивания: {str(e)}")


class UpdateDialog(QDialog):
    """Диалог проверки и установки обновлений."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Проверка обновлений")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self._init_ui()
        self._check_for_update()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        self.title_label = QLabel("Проверка обновлений...")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Иконка статуса
        self.status_icon = QLabel("⏳")
        self.status_icon.setFont(QFont("Segoe UI", 48))
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_icon)
        
        # Описание
        self.description_label = QLabel("")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        
        # Детали обновления
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)
        self.details_text.setVisible(False)
        layout.addWidget(self.details_text)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #16213e;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e94560, stop:1 #0f3460);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Прогресс текст
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.install_btn = QPushButton("Установить")
        self.install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_btn.setVisible(False)
        self.install_btn.clicked.connect(self._install_update)
        btn_layout.addWidget(self.install_btn)
        
        self.later_btn = QPushButton("Позже")
        self.later_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.later_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.later_btn)
        
        layout.addLayout(btn_layout)
    
    def _check_for_update(self):
        """Запускает проверку обновлений."""
        self.thread = UpdateCheckThread()
        self.thread.finished.connect(self._on_update_available)
        self.thread.error.connect(self._on_check_error)
        self.thread.start()
    
    def _on_update_available(self, update_info: dict):
        """Обработка результата проверки."""
        if update_info:
            # Новая версия доступна
            self.title_label.setText("Доступно обновление!")
            self.status_icon.setText("🎉")
            
            version = update_info["version"]
            published = format_date(update_info.get("published_at", ""))
            
            self.description_label.setText(
                f"Версия {version} ({published})"
            )
            
            # Показываем детали
            self.details_text.setVisible(True)
            self.details_text.setHtml(f"""
                <div style='color: #b8b8d4; line-height: 1.6;'>
                    <b>Что нового:</b><br>
                    {update_info['changelog'].replace(chr(10), '<br>')}
                </div>
            """)
            
            # Показываем прогресс и кнопку
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            self.install_btn.setVisible(True)
            
            self._update_info = update_info
        else:
            # Обновлений нет
            self.title_label.setText("Всё обновлено!")
            self.status_icon.setText("✅")
            self.description_label.setText(
                f"У вас установлена последняя версия {APP_VERSION}"
            )
            self.later_btn.setText("OK")
    
    def _on_check_error(self, error_msg: str):
        """Обработка ошибки проверки."""
        self.title_label.setText("Не удалось проверить")
        self.status_icon.setText("❌")
        self.description_label.setText(
            "Проверьте подключение к интернету и попробуйте позже"
        )
        self.details_text.setVisible(True)
        self.details_text.setText(f"<pre>{error_msg}</pre>")
    
    def _install_update(self):
        """Запускает скачивание и установку."""
        update_info = self._update_info
        
        # Показываем прогресс
        self.install_btn.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Скачивание обновления...")
        
        self.download_thread = DownloadUpdateThread(update_info["download_url"])
        self.download_thread.progress.connect(self._on_download_progress)
        self.download_thread.finished.connect(self._on_download_complete)
        self.download_thread.error.connect(self._on_download_error)
        self.download_thread.start()
    
    def _on_download_progress(self, current: int, total: int):
        """Обработка прогресса скачивания."""
        percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        
        size_current = format_size(current)
        size_total = format_size(total)
        self.progress_label.setText(
            f"{percent}% ({size_current}/{size_total})"
        )
    
    def _on_download_complete(self, file_path: str):
        """Обработка завершения скачивания."""
        self.progress_bar.setValue(100)
        self.progress_label.setText("Готово! Запуск установки...")
        
        # Закрываем диалог
        self.accept()
        
        # Запускаем установщик
        import subprocess
        try:
            subprocess.Popen([file_path, "/S"])
            # Закрываем приложение
            import sys
            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось запустить установку:\n{str(e)}"
            )
    
    def _on_download_error(self, error_msg: str):
        """Обработка ошибки скачивания."""
        self.progress_bar.setValue(0)
        self.progress_label.setText("Ошибка!")
        self.install_btn.setVisible(True)
        
        QMessageBox.critical(
            self, "Ошибка скачивания",
            f"Не удалось скачать обновление:\n{error_msg}"
        )
