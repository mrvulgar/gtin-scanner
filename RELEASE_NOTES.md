## Unreleased

### Added / Добавлено
- Debug logging via environment variable `GTIN_LOG_LEVEL` (e.g., `DEBUG`).
- Поддержка подробного логирования через переменную окружения `GTIN_LOG_LEVEL` (например, `DEBUG`).

---

## v0.1.0 — Initial release / Первый релиз

    ### English

    - **Highlights**:
    - Initial public release of a lightweight GTIN scanner app.
    - Live scanning app: `gtin_scanner_live.py`.
    - Windows hosting helper: `gtin_scanner_live_iis.py`.
    - Containerization: `Dockerfile`, `deploy/docker-compose.app.yml`, `deploy/docker-compose.traefik.yml`.
    - Curated `.gitignore` to exclude logs, PDFs, images, CSVs, and virtualenvs.
    - Dependencies listed in `requirements.txt`.

    - **Quick start**
    - Python:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python gtin_scanner_live.py
    ```
    - Docker:
    ```bash
    docker build -t gtin-scanner .
    docker run --rm -p 7860:7860 gtin-scanner
    # or
    docker compose -f deploy/docker-compose.app.yml up -d
    ```

    - **Notes**
    - The `old/` directory contains earlier scripts, Windows packaging assets, and docs.
    - Performance on very large PDFs/images depends on system resources.
    - Logs and generated artifacts are ignored by Git.

Repository: https://github.com/mrvulgar/gtin-scanner

    ### Русский

    - **Основное**:
    - Первый публичный релиз лёгкого приложения для сканирования GTIN.
    - Приложение для «живого» сканирования: `gtin_scanner_live.py`.
    - Помощник для хостинга на Windows/IIS: `gtin_scanner_live_iis.py`.
    - Контейнеризация: `Dockerfile`, `deploy/docker-compose.app.yml`, `deploy/docker-compose.traefik.yml`.
    - Обновлённый `.gitignore` (исключены логи, PDF, изображения, CSV, виртуальные окружения).
    - Зависимости перечислены в `requirements.txt`.

    - **Быстрый старт**
    - Python:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python gtin_scanner_live.py
    ```
    - Docker:
    ```bash
    docker build -t gtin-scanner .
    docker run --rm -p 7860:7860 gtin-scanner
    # или
    docker compose -f deploy/docker-compose.app.yml up -d
    ```

    - **Примечания**
    - Каталог `old/` содержит ранние скрипты, файлы для сборки под Windows и документацию.
    - Производительность на очень больших PDF/изображениях зависит от ресурсов системы.
    - Логи и генерируемые файлы не попадают в Git.

Репозиторий: https://github.com/mrvulgar/gtin-scanner


