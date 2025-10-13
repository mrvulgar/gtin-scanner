### Деплой GTIN Scanner в Docker на Ubuntu

Это инструкция по развёртыванию веб‑приложения `gtin_scanner_live.py` в Docker с Traefik (HTTPS, автоматические сертификаты), без конфликтов с другими контейнерами (например, n8n).

### Требования
- Ubuntu 22.04/24.04 с доступом `sudo`
- Открыты порты 80 и 443 на сервере/фаерволе
- DNS `scan.beerzavod.ru` указывает на IP сервера

### Быстрый деплой
1. Скопируйте проект на сервер (через `git clone` или `rsync`).
2. На сервере, в каталоге проекта, выполните:
```bash
sudo SCAN_DOMAIN=scan.beerzavod.ru TRAEFIK_ACME_EMAIL=admin@scan.beerzavod.ru bash deploy/deploy.sh
```
Скрипт:
- установит Docker, если его нет
- создаст общую сеть `proxy` для реверс‑прокси Traefik
- развернёт Traefik (80/443) и приложение на `https://scan.beerzavod.ru`

Проверка:
```bash
docker ps
# Откройте https://scan.beerzavod.ru в браузере
```

### Переменные окружения (необязательно)
Их можно передать перед запуском `deploy.sh`:
- `SCAN_DOMAIN` — публичный домен приложения (по умолчанию `scan.beerzavod.ru`)
- `TRAEFIK_ACME_EMAIL` — email для Let's Encrypt (по умолчанию `admin@scan.beerzavod.ru`)
- `APP_DIR` — каталог установки на сервере (по умолчанию `/opt/gtin-csv`)
- `TRAEFIK_NETWORK` — имя общей сети для Traefik (по умолчанию `proxy`)
- `TRAEFIK_FILES_PATH` — каталог для хранения сертификатов ACME (по умолчанию `/opt/traefik`)

Пример:
```bash
sudo APP_DIR=/srv/gtin-csv SCAN_DOMAIN=scan.beerzavod.ru bash deploy/deploy.sh
```

### Обновление/переустановка
Повторный запуск `deploy/deploy.sh` выполнит синхронизацию файлов, пересборку образа и перезапуск контейнеров:
```bash
sudo bash deploy/deploy.sh
```

### Совместная работа с другими контейнерами (например, n8n)
Traefik развёрнут как общий реверс‑прокси на сети `proxy` и слушает 80/443. Любые другие приложения подключайте к этой же сети и описывайте домен/правила через метки (labels). Пример `docker-compose` для n8n:
```yaml
version: "3.8"
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    environment:
      - N8N_PORT=5678
    labels:
      - traefik.enable=true
      - traefik.http.routers.n8n.rule=Host(`n8n.beerzavod.ru`)
      - traefik.http.routers.n8n.entrypoints=websecure
      - traefik.http.routers.n8n.tls.certresolver=le
      - traefik.http.services.n8n.loadbalancer.server.port=5678
    networks:
      - proxy
networks:
  proxy:
    external: true
```
Важно: порты 80/443 заняты Traefik. Остальные контейнеры порты наружу не публикуют — доступ идёт через домены и Traefik.

### Траблшутинг
- Сертификат не выдан: проверьте, что DNS домена указывает на сервер и порт 80 доступен снаружи. Логи Traefik: `docker logs traefik`.
- Сайт не открывается: проверьте контейнеры `docker ps`, логи приложения `docker logs gtin-scanner`.
- Порты 80/443 заняты: остановите/удалите сервисы (Nginx/Apache), которые заняли порты, до запуска Traefik.
- Повторная сборка без кэша: `docker compose -f deploy/docker-compose.app.yml build --no-cache` (из каталога `deploy` с тем же `.env`).

### Как это устроено
- `deploy/docker-compose.traefik.yml` — Traefik с автоматическими сертификатами (HTTP‑01), сеть `proxy`.
- `deploy/docker-compose.app.yml` — приложение, доступное по домену через Traefik.
- `Dockerfile` — образ Python 3.11 с зависимостями, запуск через `uvicorn gtin_scanner_live_iis:app` на `:7860`.
- `deploy/deploy.sh` — всё‑в‑одном: установка Docker, сеть, Traefik, деплой приложения.

