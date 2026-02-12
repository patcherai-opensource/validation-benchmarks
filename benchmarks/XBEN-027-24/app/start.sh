#!/bin/bash
set -e

# Write the flag from environment variable to file if provided at runtime
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag
    unset FLAG
fi

# Make the flag file readable for initial DB seeding
if [ -f /flag ]; then
    chmod 644 /flag
fi

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PASSWORD="${DB_PASSWORD:-superset_analytics}"
DB_USER="${DB_USER:-root}"

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h "$DB_HOST" --password="$DB_PASSWORD" -u "$DB_USER" --silent 2>/dev/null; do
    echo "MySQL is unavailable - sleeping"
    sleep 5
done
echo "MySQL is ready!"

# Start Apache in background
/usr/sbin/apache2ctl -D FOREGROUND &
APACHE_PID=$!

# Wait for the application to initialize and seed the flag into the DB
sleep 15

# Remove the flag file since it is now only in the database
rm -f /flag

# Wait for Apache process
wait $APACHE_PID
