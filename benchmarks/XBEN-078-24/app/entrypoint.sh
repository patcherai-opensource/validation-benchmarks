#!/bin/bash

MYSQL_HOST=${MYSQL_HOST:-localhost}
while ! nc -z "$MYSQL_HOST" 3306; do
  echo "Waiting for MySQL to start..."
  sleep 1
done

echo "Initializing database..."
sed "s/@FLAG@/${FLAG}/g" /app/db_init.sql | mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE"
echo "Database initialized."

apache2-foreground
