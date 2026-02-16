#!/bin/bash

# Set default values if environment variables are not set
MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-cmsDB}

# Wait for MySQL
while ! nc -z $MYSQL_HOST 3306; do
  echo "Waiting for MySQL to start..."
  sleep 1
done

echo "Initializing database..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE" < /app/db_init.sql
echo "Database initialized."

# Start Apache in the foreground
apache2-foreground
