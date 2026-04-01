#!/bin/sh

set -e

APP_PORT="${PORT:-8000}"
UWSGI_BUFFER_SIZE="${UWSGI_BUFFER_SIZE:-65535}"

python manage.py wait_for_db
python manage.py collectstatic --noinput

uwsgi \
  --http-socket "0.0.0.0:${APP_PORT}" \
  --master \
  --enable-threads \
  --buffer-size "${UWSGI_BUFFER_SIZE}" \
  --module app.wsgi
