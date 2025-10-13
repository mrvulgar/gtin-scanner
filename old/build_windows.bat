@echo off
REM ========================================
REM Скрипт сборки GTIN Scanner Live для Windows
REM ========================================

echo ========================================
echo GTIN Scanner Live - Windows Build Script
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден! Установите Python 3.8 или выше.
    pause
    exit /b 1
)

echo [1/5] Проверка Python... OK
echo.

REM Создаем виртуальное окружение если его нет
if not exist "venv_build" (
    echo [2/5] Создание виртуального окружения...
    python -m venv venv_build
    echo.
) else (
    echo [2/5] Виртуальное окружение уже существует... OK
    echo.
)

REM Активируем виртуальное окружение
echo [3/5] Активация виртуального окружения...
call venv_build\Scripts\activate.bat
echo.

REM Устанавливаем зависимости
echo [4/5] Установка зависимостей...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
echo.

REM Собираем приложение
echo [5/5] Сборка приложения с PyInstaller...
pyinstaller build_windows.spec --clean --noconfirm
echo.

REM Проверяем результат
if exist "dist\GTIN_Scanner_Live\GTIN_Scanner_Live.exe" (
    echo ========================================
    echo [SUCCESS] Сборка завершена успешно!
    echo ========================================
    echo.
    echo Исполняемый файл находится в:
    echo dist\GTIN_Scanner_Live\
    echo.
    echo Запустите GTIN_Scanner_Live.exe для проверки
    echo.
) else (
    echo [ERROR] Ошибка при сборке приложения!
    pause
    exit /b 1
)

pause

