#!/bin/bash

# Set default values for environment variables if not provided
MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-blogDB}
FLAG=${FLAG:-"FLAG{placeholder}"}

# Substitute flag in SQL file at runtime
sed "s|@FLAG@|$FLAG|g" /app/db_init.sql > /tmp/db_init_with_flag.sql

# Wait for MySQL
while ! nc -z $MYSQL_HOST 3306; do
  echo "Waiting for MySQL to start..."
  sleep 1
done

echo "Initializing database..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE" < /tmp/db_init_with_flag.sql
echo "Database initialized."

# Clear the flag from the environment so it's not accessible via /proc/self/environ
unset FLAG
# Also remove the temp SQL file
rm -f /tmp/db_init_with_flag.sql

# Start Apache in the foreground
apache2-foreground
