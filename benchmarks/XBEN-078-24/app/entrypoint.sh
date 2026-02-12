#!/bin/bash

# Wait for MySQL to be accepting connections
MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
echo "Waiting for MySQL at $MYSQL_HOST:3306..."

for i in $(seq 1 60); do
  if mysqladmin ping -h "$MYSQL_HOST" -u root -p"${MYSQL_ROOT_PASSWORD:-rootpassword}" --silent 2>/dev/null; then
    echo "MySQL is ready."
    break
  fi
  echo "MySQL not ready yet (attempt $i/60)..."
  sleep 2
done

# Additional delay for full initialization
sleep 3

echo "Initializing database..."
mysql -u root -p"${MYSQL_ROOT_PASSWORD:-rootpassword}" -h "$MYSQL_HOST" < /app/db_init.sql

if [ $? -eq 0 ]; then
  echo "Database initialized successfully."
else
  echo "Database initialization failed, retrying..."
  sleep 5
  mysql -u root -p"${MYSQL_ROOT_PASSWORD:-rootpassword}" -h "$MYSQL_HOST" < /app/db_init.sql
  echo "Database initialization retry complete."
fi

# Start Apache in the foreground
apache2-foreground
