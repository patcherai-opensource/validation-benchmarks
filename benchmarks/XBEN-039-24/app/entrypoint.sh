#!/bin/bash

# Set default values if environment variables are not set
MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-blogDB}

# Wait for MySQL
while ! nc -z $MYSQL_HOST 3306; do
  echo "Waiting for MySQL to start..."
  sleep 1
done

echo "Initializing database..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE" < /app/db_init.sql
echo "Database initialized."

# Substitute flag if FLAG environment variable is set (for runtime injection)
if [ ! -z "$FLAG" ]; then
  echo "Injecting flag at runtime..."
  sed -i "s/@FLAG@/$FLAG/g" /var/www/html/admin.php
  sed -i "s/@FLAG@/$FLAG/g" /app/db_init.sql
fi

# Start Apache in the foreground
apache2-foreground
