#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py migrate
python manage.py collectstatic --noinput

uwsgi --http :8000 --master --enable-threads --module app.wsgi

