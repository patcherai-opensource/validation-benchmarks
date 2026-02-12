#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database connection..."
max_retries=30
retry_count=0
while ! php -r "
try {
    \$host = getenv('DB_HOST') ?: '127.0.0.1';
    \$port = getenv('DB_PORT') ?: '3306';
    \$user = getenv('DB_USER') ?: 'root';
    \$pass = getenv('DB_PASSWORD') ?: 'contentflow_db';
    \$dbname = getenv('DB_NAME') ?: 'contentflow';
    new PDO(\"mysql:host=\$host;port=\$port;dbname=\$dbname\", \$user, \$pass);
    echo 'connected';
    exit(0);
} catch (Exception \$e) {
    exit(1);
}
" 2>/dev/null; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        echo "Failed to connect to database after $max_retries attempts"
        break
    fi
    echo "Database not ready, waiting... ($retry_count/$max_retries)"
    sleep 2
done

echo "Starting Apache..."
exec apache2-foreground
