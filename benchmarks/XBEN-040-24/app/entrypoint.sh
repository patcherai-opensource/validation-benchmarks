#!/bin/bash

# Wait for MySQL
MYSQL_HOST=${MYSQL_HOST:-localhost}
while ! nc -z $MYSQL_HOST 3306; do
  echo "Waiting for MySQL to start..."
  sleep 1
done

sleep 3

echo "Initializing database..."
mysql -u root -prootpassword -h $MYSQL_HOST < /app/db_init.sql
echo "Database initialized."

# Suppress server version in headers
echo "ServerTokens Prod" >> /etc/apache2/conf-enabled/security.conf
echo "ServerSignature Off" >> /etc/apache2/conf-enabled/security.conf

# Start Apache in the foreground
apache2-foreground
