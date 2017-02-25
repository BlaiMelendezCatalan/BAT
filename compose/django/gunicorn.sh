#!/bin/sh
python /app/manage.py collectstatic --settings=config.settings.production --noinput
python /app/manage.py migrate --settings=config.settings.production
/usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app