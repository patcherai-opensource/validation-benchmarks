#!/bin/bash
set -e

DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-inspector}
DB_PASSWORD=${DB_PASSWORD:-inspector_pass}
DB_NAME=${DB_NAME:-inspectorDB}

echo "Waiting for MySQL to be ready..."
until mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" &>/dev/null; do
    sleep 2
done

echo "Initializing database..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" < /app/db_init.sql 2>/dev/null || true
echo "Database initialized."

exec python3 /app/inspector.py
