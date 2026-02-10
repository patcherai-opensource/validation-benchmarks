#!/bin/bash
set -e

# Substitute flag at runtime if FLAG environment variable is provided
if [ ! -z "$FLAG" ]; then
    cp /label-studio/label_studio/core/settings/label_studio.py.template /label-studio/label_studio/core/settings/label_studio.py
    sed -i "s/@FLAG@/$FLAG/g" /label-studio/label_studio/core/settings/label_studio.py
    rm -f /label-studio/label_studio/core/settings/label_studio.py.template
fi

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
