# 🔧 Ручная сборка инсталлятора

## ❗ Проблема

Inno Setup не запускается через командную строку из-за проблем с кодировкой путей.

## ✅ Решение (3 шага)

### Шаг 1: Открой Inno Setup IDE

1. Нажми `Win + R`
2. Введи: `"C:\Program Files (x86)\Inno Setup 7\ISCC.exe"`
3. Нажми **OK**

**ИЛИ** найди в меню Пуск:
- **Inno Setup 7** → **Inno Setup IDE**

### Шаг 2: Открой скрипт

1. В Inno Setup IDE нажми **File** → **Open**
2. Перейди в: `C:\Users\kot35\IdeaProjects\pomoshnik`
3. Выбери файл: `installer.iss`
4. Нажми **Open**

### Шаг 3: Собери инсталлятор

1. В меню нажми **Build** → **Compile**
2. Или нажми клавишу **F9**
3. Или нажми кнопку ✅ **Compile** на панели инструментов

### Шаг 4: Проверь результат

После успешной компиляции появится окно с сообщением:
```
Compiler exit code: 0
Setup program created in: C:\Users\kot35\IdeaProjects\pomoshnik\installer\Помощник_установщик_1.0.exe
```

Файл будет здесь:
```
C:\Users\kot35\IdeaProjects\pomoshnik\installer\Помощник_установщик_1.0.exe
```

---

## 📋 Альтернатива: Через PowerShell напрямую

Если Inno Setup IDE открывается, но компиляция не работает:

1. Открой PowerShell **от имени администратора**
2. Выполни:
```powershell
$exe = "C:\Program Files (x86)\Inno Setup 7\ISCC.exe"
$script = "C:\Users\kot35\IdeaProjects\pomoshnik\installer.iss"
Start-Process -FilePath $exe -ArgumentList $script -Wait -NoNewWindow
```

3. Проверь результат:
```powershell
dir C:\Users\kot35\IdeaProjects\pomoshnik\installer\*.exe
```

---

## 📁 Что должно быть в результате

```
installer/
└── Помощник_установщик_1.0.exe  (~66 MB)
```

Файл будет создан с текущей датой (14.11.2026).

---

## 🧪 Проверка после сборки

1. **Запусти инсталлятор:**
   ```
   installer\Помощник_установщик_1.0.exe
   ```

2. **Установи на тест:**
   - Выбери папку для установки
   - Нажми "Установить"

3. **Проверь приложение:**
   - Запусти "Помощник для написания песен"
   - Проверь все функции

4. **Загрузи на GitHub:**
   - Открой: https://github.com/Kostyaptrv/pomoshnik/releases/edit/v1.0
   - Удали старый файл `_._1.0.exe`
   - Загрузи новый `Помощник_установщик_1.0.exe` через **"choose files"**

---

## 📞 Если есть ошибки

### Ошибка: "Cannot find dist\*.exe"
**Решение:** Сначала собери через PyInstaller:
```powershell
python -m PyInstaller --clean Pomoshnik.spec
```

### Ошибка: "Cannot find app_icon.ico"
**Решение:** Проверь, что файл существует:
```
C:\Users\kot35\IdeaProjects\pomoshnik\app_icon.ico
```

### Ошибка кодировки
**Решение:** Убедись, что Inno Setup установлен в:
```
C:\Program Files (x86)\Inno Setup 7\
```

---

## ✅ Чек-лист после сборки

- [ ] Inno Setup IDE открыт
- [ ] Файл `installer.iss` загружен
- [ ] Нажато **Compile** (F9)
- [ ] Файл создан: `installer\Помощник_установщик_1.0.exe`
- [ ] Размер файла: ~66 MB
- [ ] Дата создания: сегодня
- [ ] Протестирована установка
- [ ] Загружен на GitHub

---

**Дата:** 14.11.2026
**Статус:** 🔧 Требуется ручная сборка
