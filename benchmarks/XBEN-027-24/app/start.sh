#!/bin/bash
set -e

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h "${DB_HOST:-localhost}" --password="${DB_PASSWORD:-lamp_cloud_platform}" -u "${DB_USER:-root}" --silent 2>/dev/null; do
    echo "MySQL is unavailable - sleeping"
    sleep 5
done
echo "MySQL is ready!"

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
