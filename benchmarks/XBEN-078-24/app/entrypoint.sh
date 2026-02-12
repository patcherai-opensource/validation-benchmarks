#!/bin/bash

# Wait for MySQL
MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
echo "Waiting for MySQL at $MYSQL_HOST..."
for i in $(seq 1 60); do
  if nc -z "$MYSQL_HOST" 3306 2>/dev/null; then
    echo "MySQL is ready."
    break
  fi
  if [ $i -eq 60 ]; then
    echo "Timeout waiting for MySQL."
    exit 1
  fi
  sleep 2
done

# Give MySQL a moment to fully initialize
sleep 3

echo "Initializing database..."
# Try root first (works in k8s sidecar), fall back to regular user
if mysql -u root -p"${MYSQL_ROOT_PASSWORD:-rootpassword}" -h "$MYSQL_HOST" < /app/db_init.sql 2>/dev/null; then
  echo "Database initialized with root user."
elif mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DATABASE" < /app/db_init.sql 2>/dev/null; then
  echo "Database initialized with app user."
else
  echo "Warning: Database initialization may have failed. Retrying..."
  sleep 5
  mysql -u root -p"${MYSQL_ROOT_PASSWORD:-rootpassword}" -h "$MYSQL_HOST" < /app/db_init.sql 2>/dev/null || \
  mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DATABASE" < /app/db_init.sql || \
  echo "Database initialization failed."
fi

# Remove init script after use
rm -f /app/db_init.sql

# Start Apache in the foreground
exec apache2-foreground
