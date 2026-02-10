#!/bin/bash

MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-blogDB}

while ! nc -z $MYSQL_HOST 3306; do
  sleep 1
done

if [ ! -z "$FLAG" ]; then
  sed -i "s/@FLAG@/$FLAG/g" /app/db_init.sql
fi

mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE" < /app/db_init.sql 2>/dev/null

apache2-foreground
