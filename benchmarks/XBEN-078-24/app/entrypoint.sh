#!/bin/bash

MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
while ! nc -z "$MYSQL_HOST" 3306; do
  echo "Waiting for MySQL to start..."
  sleep 1
done

sleep 2

echo "Initializing database..."
mysql -u root -p"rootpassword" -h "$MYSQL_HOST" < /app/db_init.sql
echo "Database initialized."

apache2-foreground
