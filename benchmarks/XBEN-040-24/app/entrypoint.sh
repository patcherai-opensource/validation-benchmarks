#!/bin/bash

# Wait for MySQL
MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
while ! nc -z $MYSQL_HOST 3306; do
  echo "Waiting for database connection..."
  sleep 1
done

echo "Initializing database..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h $MYSQL_HOST < /app/db_init.sql
echo "Database initialized."

# Start Apache in the foreground
apache2-foreground
