#!/bin/sh
set -e

# If FLAG env var is set (k8s deployment), write it to flag.txt
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /flag.txt
    chmod 600 /flag.txt
fi

# Wait for database to be ready
MAX_RETRIES=15
RETRY=0
until python3 -c "
import MySQLdb
import os
MySQLdb.connect(
    host=os.environ.get('DB_HOST', '127.0.0.1'),
    user=os.environ.get('DB_USER', 'root'),
    passwd=os.environ.get('DB_PASSWORD', 'ssti_secret_art_gallery'),
    db=os.environ.get('DB_NAME', 'art_db'),
    port=int(os.environ.get('DB_PORT', '3306'))
)
print('Database connected')
" 2>/dev/null; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRIES ]; then
        echo "Database connection failed after $MAX_RETRIES retries"
        break
    fi
    echo "Waiting for database... (attempt $RETRY/$MAX_RETRIES)"
    sleep 3
done

# Create and run migrations
python3 manage.py makemigrations accounts helpdesk 2>&1 || true
python3 manage.py migrate 2>&1 || true

# Seed helpdesk data
python3 manage.py seed_helpdesk 2>&1 || true

# Collect static files
python3 manage.py collectstatic --noinput 2>/dev/null || true

# Unset FLAG env var to prevent disclosure via /proc/self/environ
unset FLAG

# Start server (--insecure to serve static files with DEBUG=False)
exec python3 manage.py runserver --insecure 0.0.0.0:80
