#!/bin/bash
set -e

# Write the flag from environment variable to file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
fi

# Set proper permissions for uploads directory
mkdir -p /var/www/rosario_hr/uploads
chmod -R 755 /var/www/rosario_hr/uploads

# Use DB_HOST env var or default to 127.0.0.1 (for k8s pod localhost)
DB_HOST=${DB_HOST:-127.0.0.1}

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready at $DB_HOST..."
while ! mysqladmin ping -h "$DB_HOST" --password=idor_json_cookie_trading_platform -u root --silent 2>/dev/null; do
    echo "MySQL is unavailable - sleeping"
    sleep 5
done
echo "MySQL is ready!"

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
