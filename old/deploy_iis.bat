@echo off
REM ========================================
REM GTIN Scanner Live - IIS Deployment (BAT)
REM Вспомогательный скрипт для запуска PowerShell развертывания
REM ========================================

echo ========================================
echo GTIN Scanner Live - IIS Deployment
echo ========================================
echo.

REM Проверяем права администратора
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Требуются права администратора!
    echo Запустите этот скрипт от имени администратора
    pause
    exit /b 1
)

echo [INFO] Запуск PowerShell скрипта развертывания...
echo.

REM Запускаем PowerShell скрипт
powershell.exe -ExecutionPolicy Bypass -File "%~dp0deploy_iis.ps1"

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Развертывание завершено успешно!
) else (
    echo.
    echo [ERROR] Ошибка при развертывании
)

echo.
pause

