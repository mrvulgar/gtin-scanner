#!/usr/bin/env python3
"""
GTIN Scanner Live - IIS Adapter
Этот файл адаптирует приложение для работы на IIS через ASGI
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, str(Path(__file__).parent))

# Совместимость с Python 3.12+: модуля distutils больше нет
try:
    import distutils  # type: ignore
except Exception:
    try:
        import setuptools._distutils as _distutils  # type: ignore
        sys.modules['distutils'] = _distutils
    except Exception:
        pass

# Импортируем приложение Gradio
from gtin_scanner_live import app as gradio_app

# Создаем ASGI приложение для IIS
# Gradio уже основан на FastAPI, который является ASGI приложением
# Мы просто экспортируем внутреннее FastAPI приложение

# Получаем FastAPI приложение из Gradio
app = gradio_app.app

# Дополнительные настройки для работы за IIS
if __name__ != "__main__":
    # Настройки для продакшена
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('gtin_scanner_iis.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("GTIN Scanner Live IIS adapter initialized")

if __name__ == "__main__":
    # Для локального тестирования
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

