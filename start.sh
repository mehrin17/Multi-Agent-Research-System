#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-3000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
NGINX_CONFIG="/tmp/researchai-nginx.conf"
NGINX_TMP="/tmp/researchai-nginx"
mkdir -p "${NGINX_TMP}"/{client,proxy,fastcgi,uwsgi,scgi}

sed \
  -e "s|__PORT__|${PORT}|g" \
  -e "s|__STREAMLIT_PORT__|${STREAMLIT_PORT}|g" \
  -e "s|__APP_DIR__|${APP_DIR}|g" \
  "${APP_DIR}/nginx.conf.template" > "${NGINX_CONFIG}"

streamlit run "${APP_DIR}/app.py" \
  --server.address 127.0.0.1 \
  --server.port "${STREAMLIT_PORT}" \
  --server.headless true &
STREAMLIT_PID=$!

nginx -c "${NGINX_CONFIG}" -g 'daemon off;' &
NGINX_PID=$!

cleanup() {
  kill "${STREAMLIT_PID}" "${NGINX_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

set +e
wait -n "${STREAMLIT_PID}" "${NGINX_PID}"
STATUS=$?
set -e
cleanup
wait "${STREAMLIT_PID}" 2>/dev/null || true
wait "${NGINX_PID}" 2>/dev/null || true
exit "${STATUS}"
