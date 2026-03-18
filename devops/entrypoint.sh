#!/usr/bin/env sh
set -eu

python -m reproceso.compile_scss || true

APP_PORT="${PORT:-${DATABRICKS_APP_PORT:-8080}}"

exec gunicorn -b "0.0.0.0:${APP_PORT}" reproceso.app:app
