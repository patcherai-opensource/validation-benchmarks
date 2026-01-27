#!/bin/bash
set -e

# Substitute flag at runtime if FLAG environment variable is provided
if [ ! -z "$FLAG" ]; then
    echo "Initializing DataAnnotate platform..."
    sed -i "s/@FLAG@/$FLAG/g" /var/www/app/core/settings/settings.py
else
    echo "Warning: FLAG environment variable not set, configuration incomplete"
fi

# Function to handle shutdown gracefully
shutdown() {
    echo "Shutting down services..."
    kill -QUIT $NGINX_PID 2>/dev/null || true
    kill -QUIT $PHP_FPM_PID 2>/dev/null || true
    wait
    exit 0
}

# Trap shutdown signals
trap shutdown SIGTERM SIGINT

# Start PHP-FPM in background
php-fpm &
PHP_FPM_PID=$!

# Start nginx in background
nginx -g "daemon off;" &
NGINX_PID=$!

# Wait for any process to exit
wait -n

# If we get here, one of the processes has exited
# Kill the other process and exit
shutdown
