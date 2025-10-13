# 📂 GTIN Scanner Live - Корневой каталог проекта

## 🎯 Структура проекта

Этот проект содержит разные версии и эксперименты.

---

## ⭐ ФИНАЛЬНАЯ ВЕРСИЯ ДЛЯ ИСПОЛЬЗОВАНИЯ

### 👉 **Перейдите в каталог: `installer_package/`**

```
📦 installer_package/
   │
   ├── ⭐ START_HERE.md          ← Начните здесь!
   ├── create_installers.bat    ← Создать инсталляторы
   │
   └── Все необходимые файлы для создания инсталляторов
```

**Что там:**
- ✅ Финальная версия приложения (`gtin_scanner_live.py`)
- ✅ Скрипты создания Desktop инсталлятора
- ✅ Скрипты развертывания на IIS
- ✅ Полная документация
- ❌ Нет старых версий и тестовых файлов

---

## 📁 Что в корне проекта?

Этот каталог содержит:

### ✅ Финальная версия (используйте это!)
- **`installer_package/`** - Готовая версия для создания инсталляторов

### 🧪 Старые версии и эксперименты
- `gtin_scanner_*.py` - Старые версии приложения
- `extract_gtin_*.py` - Экспериментальные скрипты
- `analyze_*.py` - Вспомогательные скрипты
- `create_test_*.py` - Тестовые скрипты
- `*.log` - Логи разработки
- `*.pdf` - Тестовые PDF файлы
- `*.csv` - Тестовые результаты
- `*.png` - Тестовые изображения

### 🔧 Разработка
- `venv/` - Виртуальное окружение для разработки

---

## 🚀 Быстрый старт

### Я хочу создать инсталляторы

```cmd
# 1. Перейдите в финальную версию
cd installer_package

# 2. Прочитайте START_HERE.md

# 3. Запустите создание инсталляторов
create_installers.bat
```

---

### Я разработчик и хочу запустить последнюю версию

```bash
# 1. Активируйте виртуальное окружение
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 2. Запустите финальную версию
python installer_package/gtin_scanner_live.py
```

---

## 📚 Документация

Вся документация находится в **`installer_package/`**

| Файл | Назначение |
|------|-----------|
| **START_HERE.md** | **⭐ Начните здесь!** |
| README.md | Обзор проекта |
| README_Installation.md | Инструкция по установке |
| README_Windows_Desktop.md | Desktop инструкция |
| README_IIS_Deployment.md | IIS инструкция |

---

## 🗂️ История версий (в корне)

### Старые версии приложения:
```
gtin_scanner_simple.py         - Самая простая версия
gtin_scanner_progress.py       - С прогресс-баром
gtin_scanner_fast.py           - Оптимизированная версия
gtin_scanner_final.py          - Предфинальная версия
gtin_scanner_live.py          - ФИНАЛЬНАЯ ВЕРСИЯ ✅
gtin_scanner_gui.py           - GUI эксперимент
gtin_scanner_app.py           - Другой вариант GUI
gtin_scanner_interactive.py   - Интерактивная версия
gtin_scanner_click.py         - CLI версия
gtin_scanner_debug.py         - Отладочная версия
```

### Старые скрипты извлечения:
```
extract_gtin.py               - Первая версия
extract_gtin_optimized.py     - Оптимизированная
extract_gtin_fast.py          - Быстрая версия
extract_gtin_progress.py      - С прогрессом
```

---

## ✅ Что использовать?

### Для создания инсталляторов:
👉 **`installer_package/`**

### Для разработки:
👉 **`installer_package/gtin_scanner_live.py`** (последняя версия)

### Старые версии:
ℹ️ Оставлены для истории, можно удалить

---

## 🧹 Очистка проекта

Если хотите оставить только финальную версию:

```bash
# Можно удалить из корня:
# - Все gtin_scanner_*.py (кроме gtin_scanner_live.py в installer_package/)
# - Все extract_gtin_*.py
# - Все analyze_*.py
# - Все create_test_*.py
# - Все *.log, *.pdf, *.csv, *.png файлы
# - Папку venv/ (если не разрабатываете)

# Оставьте:
# - installer_package/ (финальная версия)
```

---

## 📞 Поддержка

**Все вопросы и документация в:**
```
installer_package/START_HERE.md
```

---

<div align="center">

**Перейдите в `installer_package/` для работы с финальной версией** 📦

**Удачи!** 🚀

</div>

