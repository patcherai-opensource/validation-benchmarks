#!/bin/bash

# Wait for MySQL
DB_HOST=${DB_HOST:-127.0.0.1}
while ! nc -z $DB_HOST 3306; do
  echo "Waiting for MySQL to start on $DB_HOST:3306..."
  sleep 2
done

echo "MySQL is ready!"

# Start Apache in the foreground
apache2-foreground
