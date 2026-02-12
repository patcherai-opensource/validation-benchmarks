#!/bin/bash

# Wait for MySQL to be fully ready
MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}

echo "Waiting for MySQL to be ready..."
for i in $(seq 1 60); do
  if mysqladmin ping -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent 2>/dev/null; then
    echo "MySQL is ready."
    break
  fi
  echo "MySQL not ready yet, retrying ($i/60)..."
  sleep 2
done

echo "Initializing database..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DATABASE" < /app/db_init.sql
echo "Database initialized."

# Start Apache in the foreground
apache2-foreground
