#!/bin/bash

MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-blogDB}

# Wait for MySQL to be available
echo "Waiting for database..."
for i in $(seq 1 60); do
  if nc -z $MYSQL_HOST 3306 2>/dev/null; then
    echo "Database is available."
    break
  fi
  sleep 2
done

# Initialize database schema and data
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" --database="$MYSQL_DATABASE" < /app/db_init.sql 2>/dev/null
echo "Database initialization complete."

# Start Apache
exec apache2-foreground
