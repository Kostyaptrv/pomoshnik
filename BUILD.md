# 🎵 Помощник для написания песен

PyQt6-приложение для songwriter'ов с AI-генерацией, поиском рифм и управлением песнями.

## 📦 Сборка в .exe

### Быстрый старт

```bash
cd C:\Users\kot35\IdeaProjects\pomoshnik
pyinstaller --clean Pomoshnik.spec
```

Готовый файл: `dist/Помощник.exe`

### Требования

- Python 3.14+
- PyQt6
- fpdf2
- PyInstaller

```bash
pip install PyQt6 fpdf2 pyinstaller
```

### Что включено в сборку

- ✅ Все зависимости (PyQt6, fpdf2)
- ✅ JSON-файлы с данными (`data/*.json`)
- ✅ QSS-темы (`assets/qss/*.qss`)
- ✅ Иконка приложения (`app_icon.ico`)
- ✅ Без консоли (windowed mode)
- ✅ Сжатие UPX

### Структура сборки

```
dist/
└── Помощник.exe          # Готовое приложение (~50-80 MB)

build/
└── Pomoshnik/            # Временные файлы сборки
```

### Размер файла

- **С UPX**: ~50-80 MB (сжато)
- **Без UPX**: ~100-150 MB

### Обновление сборки

```bash
pyinstaller --clean --distpath dist Pomoshnik.spec
```

## 🚀 Использование

Просто запустите `Помощник.exe` — Python не нужен!

Все данные сохраняются в:
```
data/
├── favorites.json
├── search_history.json
├── custom_phrases.json
├── app_state.json
├── rhymes_dict.json
├── templates.json
└── logs/
    └── app_YYYYMMDD.log
```

## 📋 Функции

- ✍️ Пошаговый мастер создания песен
- 🔤 Поиск рифм по слову и окончанию
- 🤖 AI-генерация строк с учётом схемы рифмовки
- 📚 Библиотека фраз по категориям
- 📄 Экспорт в PDF и TXT
- 🎨 Светлая и тёмная тема
- 💾 Автосохранение
- 📋 Клонирование и управление песнями

## 🛠 Разработка

Запуск из кода:
```bash
python main_pyqt.py
```

Сборка с консолью (для отладки):
```bash
pyinstaller --clean --console Pomoshnik.spec
```

## 📝 Лицензия

MIT
