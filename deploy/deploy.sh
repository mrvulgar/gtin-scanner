#!/usr/bin/env bash
set -euo pipefail

# This script installs Docker if missing, creates a shared proxy network,
# brings up Traefik with HTTPS, and deploys the GTIN scanner app.

APP_DIR=${APP_DIR:-/opt/gtin-csv}
TRAEFIK_FILES_PATH=${TRAEFIK_FILES_PATH:-/opt/traefik}
TRAEFIK_NETWORK=${TRAEFIK_NETWORK:-proxy}
SCAN_DOMAIN=${SCAN_DOMAIN:-scan.beerzavod.ru}
TRAEFIK_ACME_EMAIL=${TRAEFIK_ACME_EMAIL:-admin@scan.beerzavod.ru}

echo "==> Deploying GTIN scanner to ${SCAN_DOMAIN}"

require_root() {
  if [[ $(id -u) -ne 0 ]]; then
    echo "Please run as root or with sudo" >&2
    exit 1
  fi
}

install_docker() {
  if command -v docker >/dev/null 2>&1; then
    echo "Docker already installed"
    return
  fi
  echo "Installing Docker..."
  # Non-interactive Docker install for Ubuntu
  apt-get update
  apt-get install -y ca-certificates curl gnupg lsb-release
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
}

ensure_network() {
  if ! docker network inspect "${TRAEFIK_NETWORK}" >/dev/null 2>&1; then
    docker network create "${TRAEFIK_NETWORK}"
  else
    echo "Docker network ${TRAEFIK_NETWORK} already exists"
  fi
}

prepare_dirs() {
  mkdir -p "${APP_DIR}"
  mkdir -p "${TRAEFIK_FILES_PATH}"
  chmod 700 "${TRAEFIK_FILES_PATH}"
  touch "${TRAEFIK_FILES_PATH}/acme.json"
  chmod 600 "${TRAEFIK_FILES_PATH}/acme.json"
}

write_env_file() {
  cat >"${APP_DIR}/.env" <<EOF
SCAN_DOMAIN=${SCAN_DOMAIN}
TRAEFIK_ACME_EMAIL=${TRAEFIK_ACME_EMAIL}
TRAEFIK_FILES_PATH=${TRAEFIK_FILES_PATH}
TRAEFIK_NETWORK=${TRAEFIK_NETWORK}
EOF
}

copy_project() {
  echo "Syncing project files to ${APP_DIR}"
  rsync -a --delete --exclude 'venv' --exclude '.git' ./ "${APP_DIR}/"
}

compose_up() {
  echo "Bringing up Traefik..."
  (
    cd "${APP_DIR}/deploy" \
    && docker compose --env-file "${APP_DIR}/.env" -f docker-compose.traefik.yml pull \
    && docker compose --env-file "${APP_DIR}/.env" -f docker-compose.traefik.yml up -d
  )
  echo "Building (with pull) and starting app..."
  (
    cd "${APP_DIR}/deploy" \
    && docker compose --env-file "${APP_DIR}/.env" -f docker-compose.app.yml build --pull \
    && docker compose --env-file "${APP_DIR}/.env" -f docker-compose.app.yml up -d
  )
}

post_check() {
  echo "==> Deployment complete. Checking containers:"
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
  echo "If DNS already points to ${SCAN_DOMAIN}, HTTPS should be issued automatically by Traefik within a minute."
}

require_root
install_docker
ensure_network
prepare_dirs
copy_project
write_env_file
compose_up
post_check

