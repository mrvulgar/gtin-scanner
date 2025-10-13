# GTIN Scanner Live - IIS Deployment Guide

## 🌐 Развертывание на IIS (Internet Information Services)

Это руководство описывает процесс развертывания **GTIN Scanner Live** на веб-сервере IIS для доступа через интернет/интранет.

---

## 🎯 Обзор

### Что такое IIS развертывание?

IIS развертывание позволяет:
- ✅ Запустить приложение как веб-сервис
- ✅ Получить доступ из любой точки сети
- ✅ Поддерживать множество одновременных пользователей
- ✅ Интегрироваться с корпоративной инфраструктурой

### Архитектура

```
[Браузер] → [IIS] → [HttpPlatformHandler] → [Python/Uvicorn] → [Gradio App]
```

---

## 📋 Системные требования

### Сервер

- **ОС:** Windows Server 2016+ или Windows 10/11 Pro
- **IIS:** 10.0+
- **RAM:** Минимум 4 GB (рекомендуется 8 GB)
- **Процессор:** 2+ ядра
- **Место на диске:** 2 GB свободного места

### Программное обеспечение

1. **IIS с компонентами:**
   - Web Server (IIS)
   - Application Development Features
   - WebSocket Protocol
   - Application Initialization

2. **Python 3.8+**
   - [Скачать с python.org](https://www.python.org/downloads/)

3. **HttpPlatformHandler v2**
   - [Скачать с IIS.net](https://www.iis.net/downloads/microsoft/httpplatformhandler)

4. **URL Rewrite Module** (для WebSocket)
   - [Скачать с IIS.net](https://www.iis.net/downloads/microsoft/url-rewrite)

---

## 🚀 Быстрая установка (автоматическая)

### Шаг 1: Подготовка файлов

1. **Скопируйте все файлы проекта** на сервер:
   ```
   C:\inetpub\wwwroot\gtin-scanner-source\
   ```

2. **Убедитесь, что присутствуют файлы:**
   - `gtin_scanner_live.py`
   - `gtin_scanner_live_iis.py`
   - `web.config`
   - `requirements.txt`
   - `deploy_iis.bat`
   - `deploy_iis.ps1`

### Шаг 2: Установка зависимостей IIS

1. **Откройте PowerShell от имени администратора**

2. **Установите компоненты IIS:**
   ```powershell
   Install-WindowsFeature -Name Web-Server,Web-WebSockets,Web-AppInit
   ```

3. **Установите HttpPlatformHandler:**
   - Скачайте с [https://www.iis.net/downloads/microsoft/httpplatformhandler](https://www.iis.net/downloads/microsoft/httpplatformhandler)
   - Запустите инсталлятор

4. **Установите URL Rewrite:**
   - Скачайте с [https://www.iis.net/downloads/microsoft/url-rewrite](https://www.iis.net/downloads/microsoft/url-rewrite)
   - Запустите инсталлятор

### Шаг 3: Автоматическое развертывание

1. **Запустите скрипт развертывания от имени администратора:**
   ```cmd
   cd C:\inetpub\wwwroot\gtin-scanner-source
   deploy_iis.bat
   ```

2. **Дождитесь завершения** (5-10 минут)

3. **Проверьте результат:**
   - Откройте браузер
   - Перейдите на `http://localhost`
   - Должен открыться интерфейс GTIN Scanner Live

### Шаг 4: Настройка (опционально)

**Изменение порта:**
```powershell
.\deploy_iis.ps1 -Port 8080
```

**Настройка доменного имени:**
```powershell
.\deploy_iis.ps1 -HostName "scanner.yourcompany.com" -Port 80
```

**Пользовательский путь:**
```powershell
.\deploy_iis.ps1 -PhysicalPath "D:\WebApps\gtin-scanner"
```

---

## 🔧 Ручная установка (подробная)

### Шаг 1: Установка IIS компонентов

#### Через Server Manager (Windows Server)

1. **Откройте Server Manager**
2. **Add Roles and Features**
3. **Выберите "Web Server (IIS)"**
4. **Добавьте компоненты:**
   - Application Development → WebSocket Protocol
   - Management Tools → IIS Management Console

#### Через PowerShell

```powershell
# Устанавливаем IIS с необходимыми компонентами
Install-WindowsFeature -Name Web-Server `
    -IncludeAllSubFeature `
    -IncludeManagementTools

# Устанавливаем дополнительные компоненты
Install-WindowsFeature -Name Web-WebSockets
Install-WindowsFeature -Name Web-AppInit
```

### Шаг 2: Установка Python

1. **Скачайте Python 3.8+**
   - [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Установите Python:**
   - ☑️ "Add Python to PATH"
   - ☑️ "Install for all users"

3. **Проверьте установку:**
   ```cmd
   python --version
   pip --version
   ```

### Шаг 3: Подготовка файлов приложения

1. **Создайте директорию:**
   ```cmd
   mkdir C:\inetpub\wwwroot\gtin-scanner
   cd C:\inetpub\wwwroot\gtin-scanner
   ```

2. **Скопируйте файлы проекта:**
   - `gtin_scanner_live.py`
   - `gtin_scanner_live_iis.py`
   - `web.config`
   - `requirements.txt`

3. **Создайте виртуальное окружение:**
   ```cmd
   python -m venv venv
   ```

4. **Активируйте и установите зависимости:**
   ```cmd
   venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Шаг 4: Настройка web.config

1. **Откройте `web.config`**

2. **Проверьте путь к Python:**
   ```xml
   <httpPlatform processPath="C:\inetpub\wwwroot\gtin-scanner\venv\Scripts\python.exe"
   ```

3. **Проверьте аргументы:**
   ```xml
   arguments="-m uvicorn gtin_scanner_live_iis:app --host 0.0.0.0 --port %HTTP_PLATFORM_PORT%"
   ```

### Шаг 5: Создание Application Pool

1. **Откройте IIS Manager:**
   - Пуск → inetmgr

2. **Создайте новый Application Pool:**
   - Правый клик на "Application Pools" → Add Application Pool
   - Name: `GTIN-Scanner-Pool`
   - .NET CLR version: `No Managed Code`
   - Managed pipeline mode: `Integrated`

3. **Настройте Application Pool:**
   - Правый клик → Advanced Settings
   - Start Mode: `AlwaysRunning`
   - Idle Time-out: `0`

### Шаг 6: Создание сайта

1. **В IIS Manager:**
   - Правый клик на "Sites" → Add Website

2. **Заполните параметры:**
   - Site name: `GTIN-Scanner`
   - Application pool: `GTIN-Scanner-Pool`
   - Physical path: `C:\inetpub\wwwroot\gtin-scanner`
   - Binding:
     - Type: `http`
     - IP address: `All Unassigned`
     - Port: `80`
     - Host name: (оставьте пустым или укажите домен)

3. **Примените настройки**

### Шаг 7: Настройка прав доступа

1. **Откройте свойства папки:**
   ```
   C:\inetpub\wwwroot\gtin-scanner
   ```

2. **Security → Edit → Add:**
   - Добавьте пользователя: `IIS AppPool\GTIN-Scanner-Pool`
   - Права: `Full Control`

### Шаг 8: Создание папки для логов

```cmd
mkdir C:\inetpub\wwwroot\gtin-scanner\logs
```

### Шаг 9: Запуск и тестирование

1. **Запустите сайт в IIS Manager:**
   - Выберите сайт `GTIN-Scanner`
   - Правый клик → Manage Website → Start

2. **Откройте браузер:**
   - Перейдите на `http://localhost`
   - Должен загрузиться интерфейс GTIN Scanner Live

3. **Проверьте логи:**
   - `C:\inetpub\wwwroot\gtin-scanner\logs\stdout.log`
   - `C:\inetpub\wwwroot\gtin-scanner\gtin_scanner_iis.log`

---

## 🔒 Безопасность и SSL

### Настройка HTTPS

#### Шаг 1: Получите SSL сертификат

**Вариант A: Self-signed (для тестирования)**
```powershell
New-SelfSignedCertificate -DnsName "scanner.yourcompany.com" -CertStoreLocation "cert:\LocalMachine\My"
```

**Вариант B: Let's Encrypt (для продакшена)**
- Используйте [win-acme](https://www.win-acme.com/)

**Вариант C: Коммерческий сертификат**
- Купите у CA (Comodo, DigiCert, и т.д.)

#### Шаг 2: Привяжите сертификат к сайту

1. **В IIS Manager:**
   - Выберите сайт → Bindings → Add

2. **Настройте HTTPS:**
   - Type: `https`
   - Port: `443`
   - SSL certificate: выберите ваш сертификат

3. **Примените**

#### Шаг 3: Перенаправление HTTP → HTTPS (опционально)

Добавьте в `web.config`:
```xml
<rewrite>
  <rules>
    <rule name="HTTP to HTTPS redirect" stopProcessing="true">
      <match url="(.*)" />
      <conditions>
        <add input="{HTTPS}" pattern="off" ignoreCase="true" />
      </conditions>
      <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
    </rule>
  </rules>
</rewrite>
```

### Настройка файрвола

```powershell
# Разрешаем входящие соединения на порт 80
New-NetFirewallRule -DisplayName "GTIN Scanner HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# Разрешаем входящие соединения на порт 443
New-NetFirewallRule -DisplayName "GTIN Scanner HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

---

## 📊 Мониторинг и обслуживание

### Просмотр логов

**Логи приложения:**
```cmd
type C:\inetpub\wwwroot\gtin-scanner\logs\stdout.log
type C:\inetpub\wwwroot\gtin-scanner\gtin_scanner_iis.log
```

**Логи IIS:**
```cmd
type C:\inetpub\logs\LogFiles\W3SVC1\*.log
```

### Мониторинг производительности

**Через PowerShell:**
```powershell
# Проверка статуса сайта
Get-Website -Name "GTIN-Scanner"

# Проверка Application Pool
Get-WebAppPoolState -Name "GTIN-Scanner-Pool"

# Перезапуск Application Pool
Restart-WebAppPool -Name "GTIN-Scanner-Pool"
```

**Через IIS Manager:**
- Откройте IIS Manager
- Выберите сайт
- Смотрите статистику в правой панели

### Автоматический перезапуск

**Настройка в Application Pool:**
1. IIS Manager → Application Pools → GTIN-Scanner-Pool
2. Advanced Settings → Recycling
3. Настройте:
   - Regular Time Interval: `1740` (29 часов)
   - Specific Times: добавьте время для перезапуска

---

## 🐛 Устранение проблем

### Приложение не запускается

**Проблема:** Ошибка 500 или пустая страница

**Диагностика:**
1. Проверьте логи stdout:
   ```cmd
   type C:\inetpub\wwwroot\gtin-scanner\logs\stdout.log
   ```

2. Проверьте, что Python установлен:
   ```cmd
   C:\inetpub\wwwroot\gtin-scanner\venv\Scripts\python.exe --version
   ```

3. Проверьте права доступа:
   - Application Pool identity должен иметь полный доступ к папке

**Решение:**
```powershell
# Перезапустите Application Pool
Restart-WebAppPool -Name "GTIN-Scanner-Pool"

# Проверьте Event Viewer
eventvwr.msc
# Смотрите: Windows Logs → Application
```

### WebSocket не работает

**Проблема:** Живой прогресс не обновляется

**Решение:**
1. Убедитесь, что WebSocket установлен:
   ```powershell
   Get-WindowsFeature -Name Web-WebSockets
   ```

2. Проверьте web.config - должно быть правило для WebSocket

3. Проверьте файрвол:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 80
   ```

### Большие PDF не загружаются

**Проблема:** Ошибка при загрузке файлов > 30MB

**Решение:**
Добавьте в `web.config`:
```xml
<security>
  <requestFiltering>
    <requestLimits maxAllowedContentLength="524288000" />
  </requestFiltering>
</security>
```

### Медленная работа

**Проблема:** Приложение работает медленно

**Решение:**
1. Увеличьте ресурсы Application Pool:
   - Advanced Settings → Recycling → Private Memory Limit: `0` (unlimited)

2. Проверьте производительность сервера:
   ```powershell
   Get-Counter '\Processor(_Total)\% Processor Time'
   Get-Counter '\Memory\Available MBytes'
   ```

3. Оптимизируйте настройки Python/Uvicorn в `web.config`

---

## 🔄 Обновление приложения

### Процесс обновления

1. **Остановите сайт:**
   ```powershell
   Stop-Website -Name "GTIN-Scanner"
   ```

2. **Сделайте резервную копию:**
   ```cmd
   xcopy C:\inetpub\wwwroot\gtin-scanner C:\Backup\gtin-scanner /E /I /H
   ```

3. **Обновите файлы:**
   - Замените `gtin_scanner_live.py`
   - Замените другие измененные файлы

4. **Обновите зависимости:**
   ```cmd
   C:\inetpub\wwwroot\gtin-scanner\venv\Scripts\pip install -r requirements.txt --upgrade
   ```

5. **Запустите сайт:**
   ```powershell
   Start-Website -Name "GTIN-Scanner"
   ```

---

## 📞 Поддержка

### Полезные команды

```powershell
# Просмотр всех сайтов
Get-Website

# Просмотр всех Application Pools
Get-IISAppPool

# Перезапуск IIS
iisreset

# Проверка конфигурации web.config
%windir%\system32\inetsrv\appcmd.exe list config "GTIN-Scanner"
```

### Дополнительные ресурсы

- [IIS Documentation](https://docs.microsoft.com/en-us/iis/)
- [HttpPlatformHandler Documentation](https://docs.microsoft.com/en-us/iis/extensions/httpplatformhandler/httpplatformhandler-configuration-reference)
- [Gradio Documentation](https://www.gradio.app/docs/)

---

## 📄 Лицензия

© 2024 Your Company. Все права защищены.

