#!/bin/bash
set -e

if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
fi

DB_HOST=${DB_HOST:-localhost}
DB_PASSWORD=${DB_PASSWORD:-idor_json_cookie_trading_platform}
DB_USER=${DB_USER:-root}

echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h "$DB_HOST" --password="$DB_PASSWORD" -u "$DB_USER" --silent 2>/dev/null; do
    sleep 5
done
echo "MySQL is ready!"

exec /usr/sbin/apache2ctl -D FOREGROUND
