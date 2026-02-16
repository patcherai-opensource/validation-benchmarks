#!/bin/bash

MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}

echo "Waiting for database..."
for i in $(seq 1 60); do
  if nc -z "$MYSQL_HOST" 3306 2>/dev/null; then
    break
  fi
  sleep 1
done

sleep 3

mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" < /app/db_init.sql 2>/dev/null

rm -f /app/db_init.sql

exec apache2-foreground
