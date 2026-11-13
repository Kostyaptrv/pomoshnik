@echo off
chcp 65001 > nul
echo ============================================
echo Сборка инсталлятора: Помощник для написания песен
echo ============================================
echo.

REM Проверка PyInstaller
echo [1/3] Проверка PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Устанавливаю PyInstaller...
    pip install pyinstaller
)

REM Сборка .exe
echo.
echo [2/3] Сборка исполняемого файла...
pyinstaller --clean Pomoshnik.spec
if errorlevel 1 (
    echo.
    echo ОШИБКА: Сборка .exe не удалась!
    pause
    exit /b 1
)
echo Готово: dist\Помощник.exe

REM Проверка Inno Setup
echo.
echo [3/3] Создание инсталлятора...
set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "%INNO_PATH%" (
    "%INNO_PATH%" installer.iss
    if errorlevel 1 (
        echo.
        echo ОШИБКА: Создание инсталлятора не удалось!
        pause
        exit /b 1
    )
    echo.
    echo ============================================
    echo УСПЕХ! Инсталлятор создан:
    echo installer\Помощник_установщик_1.0.exe
    echo ============================================
) else (
    echo.
    echo Inno Setup не найден по пути: %INNO_PATH%
    echo.
    echo Для создания инсталлятора установите Inno Setup:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo А пока можно использовать портативную версию:
    echo dist\Помощник.exe
    echo.
    echo Чтобы создать инсталлятор позже, запустите:
    echo   "%INNO_PATH%" installer.iss
)

echo.
pause
