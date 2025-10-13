# 🎯 НАЧНИТЕ ЗДЕСЬ!

## Добро пожаловать в GTIN Scanner Live

Это приложение для извлечения Data Matrix кодов из PDF файлов.

---

## ⚡ Выберите ваш вариант

### Вариант A: Я хочу установить приложение на Windows

👉 **[Перейти к инструкции Windows Desktop →](README_Windows_Desktop.md)**

**Что это даст:**
- Простая установка через инсталлятор
- Приложение работает на вашем компьютере
- Не нужен сервер

**Шаги (кратко):**
1. Создайте инсталлятор: запустите `create_installers.bat`
2. Найдите `installer_output\GTIN_Scanner_Live_Setup.exe`
3. Запустите инсталлятор
4. Готово! Приложение в меню "Пуск"

---

### Вариант B: Я хочу развернуть на веб-сервере (IIS)

👉 **[Перейти к инструкции IIS Deployment →](README_IIS_Deployment.md)**

**Что это даст:**
- Доступ из браузера
- Работа по сети
- Поддержка многих пользователей

**Шаги (кратко):**
1. Создайте пакет: запустите `create_installers.bat`
2. Найдите `package_output\GTIN_Scanner_IIS_Package.zip`
3. Распакуйте на сервере
4. Запустите `deploy_iis.bat`
5. Готово! Откройте браузер на `http://localhost`

---

### Вариант C: Я разработчик, хочу запустить локально

```bash
# 1. Создайте виртуальное окружение
python -m venv venv

# 2. Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Запустите приложение
python gtin_scanner_live.py
```

Откройте браузер: `http://127.0.0.1:7860`

---

## 📚 Полная документация

| Файл | Когда читать |
|------|--------------|
| **[START_HERE.md](START_HERE.md)** | **Вы здесь - начните отсюда!** |
| [README.md](README.md) | Обзор проекта |
| [README_Installation.md](README_Installation.md) | Общая инструкция по установке |
| [README_Windows_Desktop.md](README_Windows_Desktop.md) | Подробно про Desktop |
| [README_IIS_Deployment.md](README_IIS_Deployment.md) | Подробно про IIS |
| [README_Windows.md](README_Windows.md) | Руководство пользователя |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | История версий |

---

## 🔧 Создание инсталляторов

### Все в одном

Просто запустите:
```cmd
create_installers.bat
```

Это создаст:
- `installer_output\GTIN_Scanner_Live_Setup.exe` - Desktop инсталлятор
- `package_output\GTIN_Scanner_IIS_Package.zip` - IIS пакет

### Только Desktop

```cmd
build_windows.bat
```

Затем откройте `setup_windows.iss` в Inno Setup Compiler и нажмите F9

### Только IIS пакет

Заархивируйте эти файлы в ZIP:
- `gtin_scanner_live.py`
- `gtin_scanner_live_iis.py`
- `web.config`
- `requirements.txt`
- `deploy_iis.ps1`
- `deploy_iis.bat`
- `README_IIS_Deployment.md`

---

## ❓ Нужна помощь?

### Desktop версия
- Не запускается? → См. "Устранение проблем" в [README_Windows_Desktop.md](README_Windows_Desktop.md)
- Ошибка при сканировании? → Проверьте логи в папке приложения

### IIS версия
- Ошибка 500? → Проверьте `logs\stdout.log`
- WebSocket не работает? → Установите URL Rewrite Module

### Общие вопросы
- Читайте раздел "Устранение проблем" в соответствующей документации
- Проверяйте логи приложения
- Убедитесь, что все требования выполнены

---

## 📋 Быстрая справка

### Системные требования

**Desktop:**
- Windows 10/11
- Python 3.8+
- 4 GB RAM

**IIS:**
- Windows Server 2016+
- IIS 10.0+
- Python 3.8+
- HttpPlatformHandler v2
- 8 GB RAM

### Зависимости

Все зависимости перечислены в `requirements.txt`:
- gradio (Web UI)
- PyMuPDF (PDF обработка)
- pylibdmtx (Data Matrix декодер)
- Pillow (Обработка изображений)

---

## 🎉 Готовы начать?

1. **Desktop?** → Запустите `create_installers.bat`
2. **IIS?** → Запустите `create_installers.bat`
3. **Разработка?** → Запустите `python gtin_scanner_live.py`

**Удачи!** 🚀

---

## 📞 Контакты

**Документация:** См. файлы README выше  
**Проблемы?** См. разделы "Устранение проблем"  
**Вопросы?** Обратитесь к администратору системы

---

<div align="center">

**Made with ❤️**

</div>

