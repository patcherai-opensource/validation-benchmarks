#!/bin/bash

# Wait for MySQL
DB_HOST=${DB_HOST:-127.0.0.1}
MAX_RETRIES=30
RETRY=0
while ! nc -z $DB_HOST 3306; do
  RETRY=$((RETRY + 1))
  if [ $RETRY -ge $MAX_RETRIES ]; then
    echo "MySQL did not become ready in time."
    exit 1
  fi
  echo "Waiting for MySQL to start on $DB_HOST:3306... ($RETRY/$MAX_RETRIES)"
  sleep 2
done

echo "MySQL is ready!"

# Start Apache in the foreground
apache2-foreground
