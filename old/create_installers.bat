@echo off
REM ========================================
REM Мастер создания инсталляторов
REM GTIN Scanner Live - Create All Installers
REM ========================================

echo ========================================
echo GTIN Scanner Live - Installers Creator
echo ========================================
echo.
echo Этот скрипт создаст:
echo   1. Windows Desktop (.exe + installer)
echo   2. IIS Package (.zip)
echo.
echo Нажмите любую клавишу для продолжения...
pause >nul
echo.

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден!
    echo Установите Python с https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python найден
echo.

REM Создаем папки для результатов
echo [INFO] Создание папок для результатов...
if not exist "installer_output" mkdir installer_output
if not exist "package_output" mkdir package_output
echo.

REM ========================================
REM 1. Создание Windows Desktop
REM ========================================
echo ========================================
echo [1/2] Создание Windows Desktop Installer
echo ========================================
echo.

echo [1.1] Запуск PyInstaller сборки...
call build_windows.bat
if errorlevel 1 (
    echo [ERROR] Ошибка при сборке с PyInstaller
    pause
    exit /b 1
)
echo.

REM Проверяем наличие Inno Setup
echo [1.2] Проверка Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_PATH%" (
    echo [WARNING] Inno Setup не найден!
    echo.
    echo Установите Inno Setup 6 с:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo После установки запустите этот скрипт снова
    echo или создайте инсталлятор вручную:
    echo 1. Откройте setup_windows.iss в Inno Setup Compiler
    echo 2. Build - Compile
    echo.
    echo Нажмите любую клавишу для продолжения с созданием IIS пакета...
    pause >nul
    goto IIS_PACKAGE
)

echo [1.3] Компиляция инсталлятора с Inno Setup...
"%INNO_PATH%" setup_windows.iss
if errorlevel 1 (
    echo [ERROR] Ошибка при компиляции инсталлятора
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Windows Desktop Installer создан!
echo Расположение: installer_output\GTIN_Scanner_Live_Setup.exe
echo.

:IIS_PACKAGE
REM ========================================
REM 2. Создание IIS Package
REM ========================================
echo ========================================
echo [2/2] Создание IIS Package
echo ========================================
echo.

echo [2.1] Подготовка файлов для IIS пакета...

REM Создаем временную папку
if exist "temp_iis_package" rmdir /s /q temp_iis_package
mkdir temp_iis_package

REM Копируем необходимые файлы
echo   - Копирование файлов приложения...
copy gtin_scanner_live.py temp_iis_package\ >nul
copy gtin_scanner_live_iis.py temp_iis_package\ >nul
copy web.config temp_iis_package\ >nul
copy requirements.txt temp_iis_package\ >nul
copy deploy_iis.ps1 temp_iis_package\ >nul
copy deploy_iis.bat temp_iis_package\ >nul
copy README_IIS_Deployment.md temp_iis_package\ >nul

REM Создаем README для пакета
echo   - Создание README...
(
echo # GTIN Scanner Live - IIS Package
echo.
echo ## Содержимое пакета:
echo.
echo - gtin_scanner_live.py - Основное приложение
echo - gtin_scanner_live_iis.py - IIS адаптер
echo - web.config - Конфигурация IIS
echo - requirements.txt - Python зависимости
echo - deploy_iis.ps1 - PowerShell скрипт развертывания
echo - deploy_iis.bat - Batch скрипт развертывания
echo - README_IIS_Deployment.md - Подробная документация
echo.
echo ## Быстрая установка:
echo.
echo 1. Распакуйте этот архив на Windows Server
echo 2. Откройте PowerShell от имени администратора
echo 3. Перейдите в папку с файлами:
echo    cd C:\path\to\extracted\files
echo 4. Запустите развертывание:
echo    .\deploy_iis.bat
echo 5. Откройте браузер: http://localhost
echo.
echo ## Документация:
echo.
echo Полная документация в файле README_IIS_Deployment.md
echo.
) > temp_iis_package\README.txt

REM Проверяем PowerShell (для создания ZIP)
echo [2.2] Создание ZIP архива...
powershell -Command "Compress-Archive -Path temp_iis_package\* -DestinationPath package_output\GTIN_Scanner_IIS_Package.zip -Force"
if errorlevel 1 (
    echo [WARNING] Не удалось создать ZIP через PowerShell
    echo Создайте ZIP вручную из папки temp_iis_package\
    goto CLEANUP
)

REM Удаляем временную папку
:CLEANUP
echo [2.3] Очистка временных файлов...
if exist "temp_iis_package" rmdir /s /q temp_iis_package

echo.
echo [SUCCESS] IIS Package создан!
echo Расположение: package_output\GTIN_Scanner_IIS_Package.zip
echo.

REM ========================================
REM Итоги
REM ========================================
echo ========================================
echo [COMPLETE] Все инсталляторы созданы!
echo ========================================
echo.
echo Результаты:
echo.

if exist "installer_output\GTIN_Scanner_Live_Setup.exe" (
    echo [OK] Windows Desktop Installer:
    echo      installer_output\GTIN_Scanner_Live_Setup.exe
    echo.
) else (
    echo [!] Windows Desktop Installer не создан
    echo     См. предыдущие ошибки
    echo.
)

if exist "package_output\GTIN_Scanner_IIS_Package.zip" (
    echo [OK] IIS Package:
    echo      package_output\GTIN_Scanner_IIS_Package.zip
    echo.
) else (
    echo [!] IIS Package не создан
    echo     См. предыдущие ошибки
    echo.
)

echo ========================================
echo.
echo Что дальше?
echo.
echo Windows Desktop:
echo   - Запустите installer_output\GTIN_Scanner_Live_Setup.exe
echo   - Следуйте инструкциям мастера установки
echo.
echo IIS Server:
echo   - Распакуйте package_output\GTIN_Scanner_IIS_Package.zip на сервере
echo   - Следуйте инструкциям в README_IIS_Deployment.md
echo.
echo ========================================
echo.
pause

