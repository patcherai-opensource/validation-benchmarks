#!/bin/bash

# Wait for MySQL
MYSQL_HOST=${MYSQL_HOST:-localhost}
echo "Waiting for MySQL at $MYSQL_HOST:3306..."

max_retries=60
retry_count=0
while ! nc -z "$MYSQL_HOST" 3306; do
  echo "Waiting for MySQL to start... (attempt $((retry_count+1))/$max_retries)"
  sleep 2
  retry_count=$((retry_count+1))
  if [ $retry_count -ge $max_retries ]; then
    echo "ERROR: MySQL did not become available within timeout"
    exit 1
  fi
done

echo "MySQL is available. Waiting a few more seconds for it to be fully ready..."
sleep 5

echo "Initializing database..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" < /app/db_init.sql
echo "Database initialized."

# Start Apache in the foreground
apache2-foreground
