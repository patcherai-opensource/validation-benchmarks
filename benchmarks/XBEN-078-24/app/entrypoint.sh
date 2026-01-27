#!/bin/bash

# Wait for MySQL
MYSQL_HOST=${MYSQL_HOST:-localhost}
while ! nc -z "$MYSQL_HOST" 3306; do
  echo "Waiting for MySQL to start..."
  sleep 1
done

echo "Initializing database..."

# Replace FLAG placeholder with actual flag value and run init script
FLAG_VALUE="${FLAG:-FLAG{placeholder}}"
sed "s/FLAG_PLACEHOLDER/${FLAG_VALUE}/g" /app/db_init.sql | mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE"

echo "Database initialized."

# Start Apache in the foreground
apache2-foreground
