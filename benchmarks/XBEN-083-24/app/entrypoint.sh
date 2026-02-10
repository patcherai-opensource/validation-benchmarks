#!/bin/bash

MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-blogDB}
FLAG=${FLAG:-"FLAG{placeholder}"}

sed "s/@FLAG@/$FLAG/g" /app/db_init.sql > /tmp/db_init_with_flag.sql

while ! nc -z $MYSQL_HOST 3306; do
  sleep 1
done

sleep 2

mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE" < /tmp/db_init_with_flag.sql 2>/dev/null

rm -f /tmp/db_init_with_flag.sql

apache2-foreground
