#!/bin/bash

DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-inspector}
DB_PASSWORD=${DB_PASSWORD:-inspector_pass}
DB_NAME=${DB_NAME:-inspectorDB}

echo "Waiting for MySQL to become available..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
sleep 3

echo "Initializing database..."
mysql -u root -p"rootpassword" -h "$DB_HOST" -P "$DB_PORT" < /app/db_init.sql 2>/dev/null || true
echo "Database initialized."

exec gunicorn \
  --bind 0.0.0.0:80 \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  main:app
