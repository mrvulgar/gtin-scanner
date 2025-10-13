# GTIN Scanner Live - Installation Guide

## 📦 Руководство по установке

Добро пожаловать в руководство по установке **GTIN Scanner Live**!

Это приложение для извлечения Data Matrix кодов из PDF файлов с живым отображением прогресса.

---

## 🎯 Выберите способ установки

### 🖥️ Windows Desktop (Десктопное приложение)

**Для кого:** Для личного использования на одном компьютере

**Преимущества:**
- ✅ Простая установка через инсталлятор
- ✅ Не требует настройки сервера
- ✅ Работает локально на вашем компьютере
- ✅ Запуск одним кликом

**Инструкции:** См. [README_Windows_Desktop.md](README_Windows_Desktop.md)

---

### 🌐 IIS Web Server (Веб-сервер)

**Для кого:** Для корпоративного использования с доступом через сеть

**Преимущества:**
- ✅ Доступ из любой точки сети
- ✅ Поддержка множества пользователей
- ✅ Централизованное управление
- ✅ Интеграция с корпоративной инфраструктурой

**Инструкции:** См. [README_IIS_Deployment.md](README_IIS_Deployment.md)

---

## 📋 Системные требования

### Минимальные требования

| Компонент | Windows Desktop | IIS Server |
|-----------|----------------|------------|
| **ОС** | Windows 10/11 | Windows Server 2016+ |
| **RAM** | 4 GB | 8 GB |
| **CPU** | Intel Core i3 | Intel Xeon / Core i5 |
| **Диск** | 500 MB | 2 GB |
| **Python** | 3.8+ | 3.8+ |
| **IIS** | - | 10.0+ |

### Рекомендуемые требования

| Компонент | Windows Desktop | IIS Server |
|-----------|----------------|------------|
| **RAM** | 8 GB | 16 GB |
| **CPU** | Intel Core i5 | Intel Xeon / Core i7 |
| **Диск** | 1 GB SSD | 10 GB SSD |

---

## 🚀 Быстрый старт

### Windows Desktop

```cmd
# 1. Скачайте инсталлятор
# 2. Запустите GTIN_Scanner_Live_Setup.exe
# 3. Следуйте инструкциям мастера
# 4. Запустите приложение из меню "Пуск"
```

**Время установки:** ~5 минут

### IIS Server

```powershell
# 1. Скопируйте файлы на сервер
# 2. Откройте PowerShell от имени администратора
# 3. Запустите:
cd C:\path\to\gtin-scanner
.\deploy_iis.bat
# 4. Откройте браузер: http://localhost
```

**Время развертывания:** ~10-15 минут

---

## 📚 Структура проекта

```
gtin-csv/
├── gtin_scanner_live.py          # Основное приложение
├── gtin_scanner_live_iis.py      # IIS адаптер
├── requirements.txt               # Python зависимости
│
├── Windows Desktop:
│   ├── build_windows.spec         # PyInstaller конфигурация
│   ├── build_windows.bat          # Скрипт сборки
│   ├── setup_windows.iss          # Inno Setup скрипт
│   └── README_Windows_Desktop.md  # Документация Desktop
│
├── IIS Server:
│   ├── web.config                 # IIS конфигурация
│   ├── deploy_iis.ps1             # PowerShell развертывание
│   ├── deploy_iis.bat             # Batch развертывание
│   └── README_IIS_Deployment.md   # Документация IIS
│
└── README_Installation.md         # Это руководство
```

---

## 🔧 Разработчикам

### Локальный запуск для разработки

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd gtin-csv

# 2. Создайте виртуальное окружение
python -m venv venv

# 3. Активируйте окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Запустите приложение
python gtin_scanner_live.py
```

### Сборка инсталляторов

**Windows Desktop:**
```cmd
# Автоматическая сборка
build_windows.bat

# Создание инсталлятора (требуется Inno Setup)
# Откройте setup_windows.iss в Inno Setup Compiler
# Build → Compile
```

**IIS Package:**
```powershell
# Создайте ZIP архив с необходимыми файлами
Compress-Archive -Path gtin_scanner_live.py, gtin_scanner_live_iis.py, web.config, requirements.txt, deploy_iis.ps1, deploy_iis.bat, README_IIS_Deployment.md -DestinationPath GTIN_Scanner_IIS.zip
```

---

## 📖 Использование приложения

### Основной рабочий процесс

1. **Загрузите PDF файл**
   - Нажмите "📁 Загрузите PDF файл"
   - Выберите PDF с Data Matrix кодами

2. **Выделите область сканирования**
   - Дважды кликните на превью
   - Первый клик - начало области
   - Второй клик - конец области

3. **Настройте параметры**
   - Укажите максимум страниц для сканирования
   - 0 = сканировать все страницы

4. **Запустите сканирование**
   - Нажмите "⚡ Начать сканирование"
   - Наблюдайте за прогрессом в реальном времени

5. **Скачайте результат**
   - После завершения скачайте CSV файл
   - Каждая строка = один Data Matrix код

---

## 🐛 Устранение проблем

### Общие проблемы

#### Python не найден

**Решение:**
```cmd
# Установите Python с python.org
# Убедитесь, что установлен в PATH
python --version
```

#### Ошибка при импорте модулей

**Решение:**
```cmd
pip install -r requirements.txt
```

#### Порт уже занят

**Решение (Desktop):**
- Измените порт в `gtin_scanner_live.py` (строка 562-567)

**Решение (IIS):**
```powershell
.\deploy_iis.ps1 -Port 8080
```

### Специфичные для Windows Desktop

См. раздел "Устранение проблем" в [README_Windows_Desktop.md](README_Windows_Desktop.md)

### Специфичные для IIS

См. раздел "Устранение проблем" в [README_IIS_Deployment.md](README_IIS_Deployment.md)

---

## 📊 Производительность

### Рекомендации по использованию

| Размер PDF | Страниц | RAM | Время обработки |
|------------|---------|-----|-----------------|
| Маленький | < 50 | 4 GB | 1-2 минуты |
| Средний | 50-200 | 8 GB | 5-10 минут |
| Большой | 200-500 | 16 GB | 15-30 минут |
| Очень большой | > 500 | 32 GB | 30+ минут |

### Оптимизация

- Начинайте с малого количества страниц для тестирования
- Используйте параметр "Максимум страниц" для ограничения
- Убедитесь, что область сканирования выбрана точно
- Закройте другие приложения для освобождения памяти

---

## 🔒 Безопасность

### Windows Desktop
- Приложение работает локально
- Данные не передаются в интернет
- PDF файлы обрабатываются на вашем компьютере

### IIS Server
- Используйте HTTPS для защиты данных
- Настройте файрвол для ограничения доступа
- Регулярно обновляйте зависимости
- См. раздел "Безопасность" в [README_IIS_Deployment.md](README_IIS_Deployment.md)

---

## 🔄 Обновления

### Проверка версии

Посмотрите в логах или в About разделе приложения

### Установка обновлений

**Desktop:**
- Скачайте новый инсталлятор
- Запустите для обновления

**IIS:**
- Следуйте инструкциям в разделе "Обновление" в [README_IIS_Deployment.md](README_IIS_Deployment.md)

---

## 📞 Поддержка

### Документация

- 📘 [README_Windows_Desktop.md](README_Windows_Desktop.md) - Подробное руководство по Desktop
- 📗 [README_IIS_Deployment.md](README_IIS_Deployment.md) - Подробное руководство по IIS

### Логи

**Desktop:**
- Расположение: рядом с exe файлом
- Файл: `gtin_scanner_live.log`

**IIS:**
- Расположение: `C:\inetpub\wwwroot\gtin-scanner\logs\`
- Файлы: `stdout.log`, `gtin_scanner_iis.log`

### Контакты

При возникновении проблем:
1. Проверьте логи
2. Прочитайте раздел "Устранение проблем"
3. Обратитесь к администратору системы

---

## 📄 Лицензия

© 2024 Your Company. Все права защищены.

---

## 🎉 Начало работы

Выберите свой вариант установки:

- 🖥️ [Windows Desktop Installation](README_Windows_Desktop.md)
- 🌐 [IIS Server Deployment](README_IIS_Deployment.md)

**Удачи в работе с GTIN Scanner Live!** 🚀

