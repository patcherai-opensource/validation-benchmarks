#!/bin/bash
set -e

# Substitute flag at runtime if FLAG environment variable is provided
if [ ! -z "$FLAG" ]; then
    echo "Initializing settings..."
    # Copy template and substitute flag
    cp /app/core/settings/settings.py.template \
       /app/core/settings/settings.py
    sed -i "s/@FLAG@/$FLAG/g" /app/core/settings/settings.py
    # Remove template to prevent direct access
    rm /app/core/settings/settings.py.template
else
    echo "Warning: FLAG environment variable not set, settings will contain placeholder"
    cp /app/core/settings/settings.py.template \
       /app/core/settings/settings.py
fi

# Clear the FLAG environment variable to prevent /proc/self/environ disclosure
unset FLAG

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
