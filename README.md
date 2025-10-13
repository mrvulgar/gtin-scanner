# GTIN Scanner / Сканер GTIN

Lightweight tools to scan and extract GTIN barcodes from images/PDFs with a simple live app and optional Docker deployment.

Лёгкий набор инструментов для сканирования и извлечения GTIN из изображений/PDF с простым live‑приложением и опциональным деплоем в Docker.

---

## Overview / Обзор

- Live app: `gtin_scanner_live.py` — local UI for scanning GTIN.
- Windows/IIS helper: `gtin_scanner_live_iis.py`.
- Containerization: `Dockerfile`, `deploy/docker-compose.app.yml`, `deploy/docker-compose.traefik.yml`.
- Release notes: `RELEASE_NOTES.md`.

- Live‑приложение: `gtin_scanner_live.py` — локальный UI для сканирования GTIN.
- Помощник для Windows/IIS: `gtin_scanner_live_iis.py`.
- Контейнеризация: `Dockerfile`, `deploy/docker-compose.app.yml`, `deploy/docker-compose.traefik.yml`.
- Описание релизов: `RELEASE_NOTES.md`.

Repository / Репозиторий: https://github.com/mrvulgar/gtin-scanner

---

## Quick start (Python) / Быстрый старт (Python)

English:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python gtin_scanner_live.py
```

Русский:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python gtin_scanner_live.py
```

---

## Quick start (Docker) / Быстрый старт (Docker)

English:
```bash
docker build -t gtin-scanner .
docker run --rm -p 7860:7860 gtin-scanner
# or compose
docker compose -f deploy/docker-compose.app.yml up -d
```

Русский:
```bash
docker build -t gtin-scanner .
docker run --rm -p 7860:7860 gtin-scanner
# или через compose
docker compose -f deploy/docker-compose.app.yml up -d
```

---

## Deployment / Деплой

- See `deploy/README_DEPLOY.md` for compose and reverse proxy examples.
- Configure TLS and ports for production.

- См. `deploy/README_DEPLOY.md` для примеров compose и reverse proxy.
- В продакшене настройте TLS и порты.

---

## Windows/IIS

- `gtin_scanner_live_iis.py` — minimal helper for IIS hosting.
- Older scripts and Windows assets are under `old/`.

- `gtin_scanner_live_iis.py` — минимальный помощник для IIS.
- Ранние скрипты и файлы для Windows находятся в `old/`.

---

## Notes / Примечания

- Performance on large PDFs/images depends on system resources.
- Logs, PDFs, images, CSVs, and virtualenvs are ignored by `.gitignore`.

- Производительность на больших PDF/изображениях зависит от ресурсов системы.
- Логи, PDF, изображения, CSV и виртуальные окружения исключены в `.gitignore`.

---

## License / Лицензия

Add a LICENSE file for open‑source distribution.

Добавьте файл LICENSE, если планируете открывать исходники.
