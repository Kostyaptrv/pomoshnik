# 🚀 Шпаргалка по проекту "Помощник для написания песен"

## ⚡ Быстрый старт

### Запуск
```powershell
cd C:\Users\kot35\IdeaProjects\pomoshnik
python main_pyqt.py
```

### Сборка .exe
```powershell
pyinstaller --clean Pomoshnik.spec
# Готово: dist/Помощник.exe
```

### Сборка инсталлятора
```powershell
.\build.ps1
# Готово: installer/Помощник_установщик_1.0.exe
```

## 📁 Где что находится

| Файл | Назначение |
|------|-----------|
| `main_pyqt.py` | Запуск приложения |
| `ui/main_window.py` | Главное окно |
| `ui/pages/editor_page.py` | Редактор песен |
| `ui/pages/rhymes_page.py` | Словарь рифм |
| `engine/phrases.py` | Библиотека фраз |
| `data/rhymes_dict.json` | Словарь рифм (~60 слов) |
| `utils/updater.py` | Автообновление |

## 🔧 Часто используемые команды

### Добавить новую фразу
```python
# engine/phrases.py, добавь в нужный список:
PHRASES["music"].append("Новая фраза про музыку")
```

### Добавить новые рифмы
```json
// data/rhymes_dict.json, добавь новый ключ:
{
  "новое_слово": ["рифм1", "рифм2", "рифм3"]
}
```

### Изменить версию
```python
# utils/updater.py, строка 13:
APP_VERSION = "1.1"  # Измени здесь
```

### Отключить автообновление
```python
# ui/main_window.py, закомментируй:
# QTimer.singleShot(2000, self._check_for_updates)
```

## 🎯 Горячие клавиши в приложении

| Клавиша | Действие |
|---------|----------|
| `Ctrl+E` | Открыть редактор |
| `Ctrl+P` | Печать/Экспорт |
| `Ctrl+F` | Поиск |
| `Ctrl+S` | Сохранить |

## 📊 Текущие данные

### Словарь рифм
- **Слов:** ~60
- **Рифм:** ~500+
- **Категории:** любовь, природа, боль, надежда, мечты, время

### Библиотека фраз
- **Фраз:** ~150+
- **Категории:** love (27), nature (25), pain (25), hope (25), dreams (25)

## 🐛 Решение проблем

### Приложение не запускается
```powershell
# Проверь Python
python --version  # Должно быть 3.14.7

# Проверь PyQt6
pip show PyQt6

# Установи зависимости
pip install -r requirements.txt
```

### Ошибка "ModuleNotFoundError"
```powershell
# Активируй venv
.venv\Scripts\activate

# Запусти
python main_pyqt.py
```

### Ошибка сборки PyInstaller
```powershell
# Очисти кэш
rmdir /s /q build
rmdir /s /q dist

# Собери заново
pyinstaller --clean Pomoshnik.spec
```

### Ошибка автообновления
1. Проверь `GITHUB_REPO` в `utils/updater.py`
2. Проверь интернет
3. Проверь логи: `data/logs/app_YYYYMMDD.log`

## 📖 Ссылки на документацию

| Файл | Описание |
|------|----------|
| `README.md` | Общая информация |
| `BUILD.md` | Инструкция по сборке |
| `UPDATER.md` | Как работает автообновление |
| `GITHUB_SETUP_RU.md` | Настройка GitHub |
| `PROJECT_STATUS.md` | Текущее состояние проекта |

## 🎨 Стилизация

### Изменить тему
```python
# ui/main_window.py, метод _load_stylesheet()
# Или через UI: кнопка "🌙 Тёмная тема" / "🌞 Светлая тема"
```

### Изменить скругление углов
```python
# Глобально: 12px (border-radius)
# В QSS: border-radius: 12px;
```

### Изменить цвета
```python
# assets/qss/dark_theme.qss
# assets/qss/light_theme.qss
```

## 🚀 Публикация обновления

```powershell
# 1. Измени версию в utils/updater.py
# 2. Закоммить
git add .
git commit -m "Версия 1.1"
git push

# 3. Пересобери
.\build.ps1

# 4. Создай релиз на GitHub
#    https://github.com/твой_ник/pomoshnik/releases/new
#    Tag: v1.1
#    Файл: installer/Помощник_установщик_1.1.exe
```

## 💡 Советы

1. **Регулярно делай бэкапы** папки `data/`
2. **Делай git commit** после каждого изменения
3. **Тестируй автообновление** на тестовом релизе
4. **Следи за логами** в `data/logs/`
5. **Используй venv** для изоляции зависимостей

## 📞 Поддержка

Если что-то не работает:
1. Проверь логи: `data/logs/app_YYYYMMDD.log`
2. Проверь подключение к интернету
3. Перезапусти приложение
4. Очисти кэш: `rmdir /s /q build && rmdir /s /q dist`

---

**Версия:** 1.0
**Последнее обновление:** 2025
**Статус:** ✅ Готово к использованию
