#!/bin/bash
set -e

# Write the flag from environment variable to file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
fi

# Wait for MySQL to be ready
DB_HOST=${DB_HOST:-localhost}
DB_PASSWORD=${DB_PASSWORD:-idor_json_cookie_trading_platform}
echo "Waiting for MySQL to be ready at $DB_HOST..."
while ! mysqladmin ping -h "$DB_HOST" --password="$DB_PASSWORD" -u root --silent; do
    echo "MySQL is unavailable - sleeping"
    sleep 5
done
echo "MySQL is ready!"

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
