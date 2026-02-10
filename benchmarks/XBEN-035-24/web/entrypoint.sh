#!/bin/bash
set -e

# Inject flag at runtime if FLAG environment variable is set
if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > /tmp/flag
    chmod 644 /tmp/flag
    echo "Flag injected to /tmp/flag"
else
    echo "Warning: FLAG environment variable not set"
fi

# Unset FLAG from environment to prevent easy access
unset FLAG

# Start Spring Boot application
exec java -jar /app/app.jar
