@echo off
chcp 65001 > nul
cd /d "C:\Users\kot35\IdeaProjects\pomoshnik"
echo Сборка инсталлятора...
"C:\Program Files (x86)\Inno Setup 7\ISCC.exe" "installer.iss"
echo.
echo Проверка результата:
dir installer\*.exe
echo.
pause
