#!/bin/sh

set -e

UWSGI_BUFFER_SIZE="${UWSGI_BUFFER_SIZE:-65535}"

python manage.py wait_for_db
python manage.py collectstatic --noinput

uwsgi \
  --http :8000 \
  --master \
  --enable-threads \
  --buffer-size "${UWSGI_BUFFER_SIZE}" \
  --module app.wsgi
