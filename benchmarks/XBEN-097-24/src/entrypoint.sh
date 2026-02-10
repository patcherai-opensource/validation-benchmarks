#!/bin/bash
set -e

# Substitute flag at runtime if FLAG environment variable is provided
if [ ! -z "$FLAG" ]; then
    sed -i "s/@FLAG@/$FLAG/g" /var/www/config/database.conf
fi

# Clear the FLAG environment variable so it cannot be accessed via /proc/self/environ
unset FLAG

# Function to handle shutdown gracefully
shutdown() {
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
