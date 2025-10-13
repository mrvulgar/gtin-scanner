# GTIN Scanner Live - Project Manifest

## 📦 Полный список файлов проекта

Этот файл содержит описание всех файлов проекта и их назначение.

---

## 🎯 Основные файлы приложения

| Файл | Описание | Назначение |
|------|----------|-----------|
| `gtin_scanner_live.py` | Основное приложение | Главный файл с Gradio интерфейсом |
| `gtin_scanner_live_iis.py` | IIS адаптер | ASGI обертка для работы на IIS |
| `requirements.txt` | Зависимости Python | Список всех необходимых библиотек |

---

## 🖥️ Windows Desktop (Инсталлятор)

| Файл | Описание | Используется для |
|------|----------|------------------|
| `build_windows.spec` | PyInstaller конфигурация | Настройка сборки exe файла |
| `build_windows.bat` | Скрипт сборки | Автоматическая сборка exe |
| `setup_windows.iss` | Inno Setup скрипт | Создание инсталлятора |
| `create_installers.bat` | Мастер сборки | Создание всех инсталляторов |

### Результаты сборки Desktop:
- `dist\GTIN_Scanner_Live\` - Папка с exe и зависимостями
- `dist\GTIN_Scanner_Live\GTIN_Scanner_Live.exe` - Исполняемый файл
- `installer_output\GTIN_Scanner_Live_Setup.exe` - Готовый инсталлятор

---

## 🌐 IIS Server (Веб-сервер)

| Файл | Описание | Используется для |
|------|----------|------------------|
| `web.config` | Конфигурация IIS | Настройка HttpPlatformHandler |
| `deploy_iis.ps1` | PowerShell скрипт | Автоматическое развертывание |
| `deploy_iis.bat` | Batch скрипт | Запуск PowerShell скрипта |

### Результаты сборки IIS:
- `package_output\GTIN_Scanner_IIS_Package.zip` - Готовый пакет для IIS

---

## 📚 Документация

| Файл | Целевая аудитория | Содержание |
|------|-------------------|-----------|
| `START_HERE.md` | **Все пользователи** | **Быстрый старт (начните здесь!)** |
| `README.md` | Все пользователи | Обзор проекта, возможности |
| `README_Installation.md` | Все пользователи | Общая инструкция по установке |
| `README_Windows_Desktop.md` | Конечные пользователи | Подробная инструкция Desktop версии |
| `README_IIS_Deployment.md` | Системные администраторы | Подробная инструкция IIS версии |
| `README_Windows.md` | Конечные пользователи | Краткое руководство пользователя |
| `RELEASE_NOTES.md` | Все пользователи | История версий и изменений |
| `MANIFEST.md` | Разработчики | Этот файл - список всех файлов |

---

## 🔧 Вспомогательные файлы

| Файл | Назначение |
|------|-----------|
| `.gitignore` | Исключения для Git |

---

## 📊 Структура папок после сборки

```
gtin-csv/
├── 📄 Основные файлы
│   ├── gtin_scanner_live.py
│   ├── gtin_scanner_live_iis.py
│   ├── requirements.txt
│   └── web.config
│
├── 🖥️ Windows Desktop
│   ├── build_windows.spec
│   ├── build_windows.bat
│   ├── setup_windows.iss
│   └── create_installers.bat
│
├── 🌐 IIS Server
│   ├── deploy_iis.ps1
│   └── deploy_iis.bat
│
├── 📚 Документация
│   ├── START_HERE.md          ⭐ Начните здесь!
│   ├── README.md
│   ├── README_Installation.md
│   ├── README_Windows_Desktop.md
│   ├── README_IIS_Deployment.md
│   ├── README_Windows.md
│   ├── RELEASE_NOTES.md
│   └── MANIFEST.md            (этот файл)
│
├── 📦 Результаты сборки (создаются автоматически)
│   ├── dist/
│   │   └── GTIN_Scanner_Live/
│   │       └── GTIN_Scanner_Live.exe
│   │
│   ├── installer_output/
│   │   └── GTIN_Scanner_Live_Setup.exe
│   │
│   └── package_output/
│       └── GTIN_Scanner_IIS_Package.zip
│
└── 🔧 Служебные (создаются при работе)
    ├── venv/                  (виртуальное окружение)
    ├── venv_build/            (для сборки)
    ├── logs/                  (логи IIS)
    └── *.log                  (логи приложения)
```

---

## 🚀 Файлы для распространения

### Desktop пользователям
Отправьте только:
- `installer_output\GTIN_Scanner_Live_Setup.exe`

### IIS администраторам
Отправьте:
- `package_output\GTIN_Scanner_IIS_Package.zip`

Содержимое ZIP:
- `gtin_scanner_live.py`
- `gtin_scanner_live_iis.py`
- `web.config`
- `requirements.txt`
- `deploy_iis.ps1`
- `deploy_iis.bat`
- `README_IIS_Deployment.md`
- `README.txt` (создается автоматически)

---

## 📝 Файлы НЕ включаемые в сборку

Эти файлы остаются только в исходном коде:

### Тестовые и вспомогательные скрипты
- `analyze_page_structure.py`
- `analyze_pdf.py`
- `create_test_datamatrix.py`
- `create_test_pdf.py`
- `extract_gtin_*.py`
- `gtin_scanner_*.py` (кроме gtin_scanner_live.py)

### Тестовые данные
- `*.pdf` (тестовые PDF файлы)
- `*.csv` (тестовые результаты)
- `*.png` (тестовые изображения)
- `*.log` (логи разработки)

### Окружения и временные файлы
- `venv/` (виртуальное окружение разработки)
- `venv_build/` (виртуальное окружение сборки)
- `__pycache__/`
- `*.pyc`

---

## 🔄 Жизненный цикл файлов

### Разработка
```
gtin_scanner_live.py (редактируется)
    ↓
requirements.txt (обновляется)
    ↓
Тестирование локально
```

### Сборка Desktop
```
create_installers.bat (запуск)
    ↓
build_windows.bat (сборка exe)
    ↓ использует build_windows.spec
dist\GTIN_Scanner_Live\*.* (создается)
    ↓
setup_windows.iss (Inno Setup)
    ↓
installer_output\GTIN_Scanner_Live_Setup.exe (результат)
```

### Сборка IIS Package
```
create_installers.bat (запуск)
    ↓
Копирование файлов во временную папку
    ↓
Создание README.txt
    ↓
Архивирование в ZIP
    ↓
package_output\GTIN_Scanner_IIS_Package.zip (результат)
```

### Развертывание Desktop
```
GTIN_Scanner_Live_Setup.exe (запуск)
    ↓
Распаковка в C:\Program Files\GTIN Scanner Live\
    ↓
Создание ярлыков
    ↓
Готово к использованию
```

### Развертывание IIS
```
GTIN_Scanner_IIS_Package.zip (распаковать)
    ↓
deploy_iis.bat (запуск)
    ↓
Создание виртуального окружения на сервере
    ↓
Установка зависимостей
    ↓
Настройка IIS
    ↓
Готово к использованию
```

---

## 📐 Размеры файлов (приблизительно)

| Компонент | Размер |
|-----------|--------|
| Исходный код (без venv) | ~1 MB |
| Desktop exe (dist/) | ~150 MB |
| Desktop инсталлятор (.exe) | ~80 MB |
| IIS Package (.zip) | ~50 KB |
| После установки Desktop | ~200 MB |
| После развертывания IIS | ~150 MB |

---

## ✅ Контрольный список для релиза

### Перед созданием инсталляторов:

- [ ] Протестирован `gtin_scanner_live.py` локально
- [ ] Обновлен `requirements.txt`
- [ ] Обновлена документация
- [ ] Проверена версия в `setup_windows.iss`
- [ ] Обновлен `RELEASE_NOTES.md`

### После создания инсталляторов:

- [ ] Протестирован Desktop инсталлятор на чистой Windows
- [ ] Протестирован IIS пакет на тестовом сервере
- [ ] Проверены все README на актуальность
- [ ] Проверены все пути в документации

### Для распространения:

- [ ] Desktop инсталлятор работает
- [ ] IIS пакет содержит все необходимые файлы
- [ ] Документация включена
- [ ] Создан changelog для пользователей

---

## 📞 Для разработчиков

### Добавление нового файла

1. Создайте файл
2. Обновите этот MANIFEST.md
3. Если нужно в инсталляторе - обновите:
   - `setup_windows.iss` (для Desktop)
   - `create_installers.bat` (для IIS)

### Изменение структуры

1. Обновите соответствующие скрипты сборки
2. Обновите документацию
3. Обновите этот MANIFEST.md
4. Протестируйте сборку

---

## 📄 История версий файлов

### Version 1.0.0 (Initial Release)
- Все файлы созданы
- Полная функциональность Desktop и IIS
- Полная документация

---

<div align="center">

**Документ актуален для версии: 1.0.0**

Последнее обновление: 2024

</div>

