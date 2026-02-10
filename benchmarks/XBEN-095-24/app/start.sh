#!/bin/bash
set -e

# Wait for MySQL to be ready
echo "Waiting for MySQL..."
max_retries=30
count=0
until php -r "new mysqli(getenv('MYSQL_HOST'), getenv('MYSQL_USER'), getenv('MYSQL_PASSWORD'), getenv('MYSQL_DATABASE'));" 2>/dev/null; do
    count=$((count+1))
    if [ $count -ge $max_retries ]; then
        echo "Failed to connect to MySQL after $max_retries attempts"
        exit 1
    fi
    echo "Waiting for MySQL... attempt $count/$max_retries"
    sleep 2
done
echo "MySQL is ready!"

# Insert flag into secrets table
php /plant_flag.php

# Start Apache
exec apache2-foreground
