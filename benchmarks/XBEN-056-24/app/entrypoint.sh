#!/bin/sh
set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"

./wait-for-it.sh "${DB_HOST}:${DB_PORT}" --timeout=60 -- echo "Database is ready"

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput 2>/dev/null || true

exec python3 manage.py runserver --insecure 0.0.0.0:80
