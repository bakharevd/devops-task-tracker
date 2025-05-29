#!/bin/bash
set -e

echo "Apply migrations..."
python manage.py migrate --noinput

echo "Collect static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2