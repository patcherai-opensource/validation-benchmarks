#!/bin/bash
set -e

echo "Waiting for database..."
MAX_TRIES=60
for i in $(seq 1 $MAX_TRIES); do
    if php -r "
        try {
            \$host = getenv('DB_HOST') ?: '127.0.0.1';
            \$port = getenv('DB_PORT') ?: '3306';
            \$user = getenv('DB_USER') ?: 'gestipro';
            \$pass = getenv('DB_PASSWORD') ?: 'gestipro';
            new PDO(\"mysql:host=\$host;port=\$port\", \$user, \$pass);
            echo 'ok';
        } catch(Exception \$e) {
            // not ready yet
        }
    " 2>/dev/null | grep -q ok; then
        echo "Database is ready."
        break
    fi
    if [ "$i" -eq "$MAX_TRIES" ]; then
        echo "Warning: Database connection timeout, starting anyway..."
    fi
    echo "Waiting... ($i/$MAX_TRIES)"
    sleep 2
done

exec apache2-foreground
