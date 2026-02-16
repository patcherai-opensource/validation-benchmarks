#!/bin/bash
set -e

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-cfadmin}"
DB_PASSWORD="${DB_PASSWORD:-cf_db_s3cure!}"
DB_NAME="${DB_NAME:-contentforge}"

echo "Waiting for database..."
for i in $(seq 1 60); do
    if mysqladmin ping -h "$DB_HOST" -P "$DB_PORT" -u root --password="${MYSQL_ROOT_PASSWORD:-rootpass123}" --silent 2>/dev/null; then
        echo "Database is ready."
        break
    fi
    sleep 2
done

echo "Initializing database..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u root --password="${MYSQL_ROOT_PASSWORD:-rootpass123}" -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';" 2>/dev/null || true
mysql -h "$DB_HOST" -P "$DB_PORT" -u root --password="${MYSQL_ROOT_PASSWORD:-rootpass123}" < /var/www/html/init_db.sql 2>/dev/null || true

exec apache2-foreground
