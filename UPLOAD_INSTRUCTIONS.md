# 📤 Загрузка файла на GitHub

## ✅ Файл переименован!

**Старое имя:** `Помощник_установщик_1.0.exe`  
**Новое имя:** `Pomoshnik_Setup_1.0.exe`

## 🎯 Загрузи файл на GitHub

### Способ 1: Через браузер (рекомендуется)

1. Открой: https://github.com/Kostyaptrv/pomoshnik/releases/edit/v1.0

2. **Удали старые файлы:**
   - Наведи на `_._1.0.exe` → нажми **✕**
   - Наведи на `installer_simple.iss` → нажми **✕**

3. **Загрузи новый файл:**
   - Перетащи файл `Pomoshnik_Setup_1.0.exe` в область загрузки
   - ИЛИ кликни по области и выбери файл

4. **Нажми "Обновить выпуск"** (зелёная кнопка внизу)

### Способ 2: Через drag-and-drop с правильным файлом

Файл находится здесь:
```
C:\Users\kot35\IdeaProjects\pomoshnik\installer\Pomoshnik_Setup_1.0.exe
```

**ВАЖНО:** Используй именно этот файл!

## 🧪 Проверка

После загрузки запусти диагностику:

```powershell
cd C:\Users\kot35\IdeaProjects\pomoshnik
python check_update.py
```

Должно показать:
```
📎 Ассеты (1 файлов):
  - Pomoshnik_Setup_1.0.exe
    Размер: 63.1 MB
    ✅ Найден установщик!
```

## 📊 Что изменено в коде

### utils/updater.py
Теперь ищет файлы с латинскими и кириллическими именами:
```python
if (asset_name.endswith(".exe") and 
    ("Pomoshnik" in asset_name or "Помощник" in asset_name)):
```

### installer.iss
```ini
OutputBaseFilename=Pomoshnik_Setup_1.0
```

## ✅ Итог

После загрузки файла автообновление будет работать! 🎉
