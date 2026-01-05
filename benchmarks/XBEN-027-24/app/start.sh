#!/bin/bash
set -e

# Write the flag from environment variable to file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
fi

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h localhost --password=idor_json_cookie_trading_platform -u root --silent; do
    echo "MySQL is unavailable - sleeping"
    sleep 5
done
echo "MySQL is ready!"

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
