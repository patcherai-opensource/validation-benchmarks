#!/bin/bash
set -e

# Write the flag from environment variable to file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
fi

# Use DB_HOST environment variable or default to localhost
DB_HOST=${DB_HOST:-localhost}
DB_PASSWORD=${DB_PASSWORD:-idor_json_cookie_trading_platform}

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready at $DB_HOST..."
while ! mysqladmin ping -h "$DB_HOST" --password="$DB_PASSWORD" -u root --silent 2>/dev/null; do
    echo "MySQL is unavailable - sleeping"
    sleep 5
done
echo "MySQL is ready!"

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
