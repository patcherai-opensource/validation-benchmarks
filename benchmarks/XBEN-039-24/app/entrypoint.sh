#!/bin/bash

MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
MYSQL_DATABASE=${MYSQL_DATABASE:-pimcore}

# Wait for MySQL to be ready
MAX_RETRIES=60
RETRY=0
while ! nc -z $MYSQL_HOST 3306; do
  RETRY=$((RETRY + 1))
  if [ $RETRY -ge $MAX_RETRIES ]; then
    echo "MySQL failed to start after $MAX_RETRIES attempts"
    exit 1
  fi
  sleep 2
done

# Additional wait for MySQL to finish initialization
sleep 5

echo "Initializing database..."
mysql -u root -prootpassword -h "$MYSQL_HOST" < /app/db_init.sql 2>/dev/null
echo "Database initialized."

# Substitute flag if FLAG environment variable is set (for runtime injection in k8s)
if [ ! -z "$FLAG" ]; then
  sed -i "s|@FLAG@|$FLAG|g" /app/db_init.sql
  mysql -u root -prootpassword -h "$MYSQL_HOST" < /app/db_init.sql 2>/dev/null
fi

# Unset FLAG from environment to prevent leaking
unset FLAG

# Start Apache in the foreground
apache2-foreground
