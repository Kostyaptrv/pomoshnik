# 🔧 Исправление автообновления - Инструкция

## 🔍 Проблема найдена!

**Диагностика показала:**
- ✅ Релиз v1.0 создан на GitHub
- ✅ Репозиторий доступен
- ❌ **Файл называется `_._1.0.exe` вместо `Помощник_установщик_1.0.exe`**

GitHub сохранил файл с неправильным именем из-за проблемы с кодировкой.

---

## ✅ РЕШЕНИЕ (3 шага)

### Шаг 1: Удали старый файл с релиза

1. Открой: https://github.com/Kostyaptrv/pomoshnik/releases/edit/v1.0
2. Найди файл `_._1.0.exe`
3. Нажми 🗑️ **Delete** рядом с файлом
4. Подтверди удаление

### Шаг 2: Пересобери инсталлятор

```powershell
cd C:\Users\kot35\IdeaProjects\pomoshnik

# Очисти старую сборку
del installer\Помощник_установщик_1.0.exe

# Пересобери
&C:\Program\ Files\ \(x86\)\Inno\ Setup\ 7\ISCC.exe installer.iss
```

**Или через PowerShell:**
```powershell
powershell -Command "cd C:\Users\kot35\IdeaProjects\pomoshnik; & 'C:\Program Files (x86)\Inno Setup 7\ISCC.exe' installer.iss"
```

### Шаг 3: Загрузи файл правильно

**ВАЖНО:** Используй веб-интерфейс GitHub, НЕ drag-and-drop!

1. Открой: https://github.com/Kostyaptrv/pomoshnik/releases/edit/v1.0
2. Найди секцию "Attach binaries" или "Attach files by dropping them below"
3. Нажми **"choose files"** (НЕ перетаскивай файл!)
4. Выбери: `installer/Помощник_установщик_1.0.exe`
5. Файл загрузится с правильным именем
6. Нажми **"Save changes"** внизу страницы

---

## 🧪 Проверка

После загрузки файла:

1. Запусти диагностику:
```powershell
cd C:\Users\kot35\IdeaProjects\pomoshnik
python check_update.py
```

2. Должно быть:
```
📎 Ассеты (1 файлов):
  - Помощник_установщик_1.0.exe
    Размер: 63.1 MB
    ✅ Найден установщик!
```

3. Пересобери приложение:
```powershell
python -m PyInstaller --clean Pomoshnik.spec
```

4. Запусти приложение и проверь автообновление

---

## 🔧 Дополнительные исправления

Также я исправил баги в коде:

### Исправление 1: utils/updater.py
- ✅ Добавлено логирование
- ✅ Улучшена обработка ошибок
- ✅ Добавлены сообщения об ошибках 404

### Исправление 2: ui/components/update_dialog.py
- ✅ Исправлен баг с `None` при "нет обновлений"
- ✅ Исправлена видимость details_text
- ✅ Добавлен импорт APP_VERSION

---

## 📋 Если всё ещё не работает

### Проверь 1: GITHUB_REPO в updater.py
```python
# utils/updater.py, строка ~16
GITHUB_REPO = "Kostyaptrv/pomoshnik"  # Должно быть так!
```

### Проверь 2: Логирование
Добавь в `main_pyqt.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Проверь 3: Ручная проверка API
```powershell
curl https://api.github.com/repos/Kostyaptrv/pomoshnik/releases/latest
```

Должно вернуть JSON с `tag_name: "v1.0"` и ассетами.

### Проверь 4: Версия приложения
```python
# utils/updater.py
APP_VERSION = "1.0"  # Должно совпадать с тегом релиза
```

---

## 🎯 Итоговый чек-лист

- [ ] Удалить старый файл `_._1.0.exe` с релиза
- [ ] Пересобрать инсталлятор
- [ ] Загрузить файл через "choose files" (не drag-drop!)
- [ ] Проверить имя файла на GitHub
- [ ] Запустить `python check_update.py`
- [ ] Пересобрать приложение (PyInstaller)
- [ ] Протестировать автообновление

---

## 📞 Если нужна помощь

1. Запусти: `python check_update.py`
2. Скопируй вывод
3. Проверь логи: `data/logs/app_YYYYMMDD.log`
4. Отправь вывод и логи для диагностики

---

**Дата:** 14.11.2026
**Статус:** 🔧 В процессе исправления
