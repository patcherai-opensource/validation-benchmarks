#!/bin/bash
set -e

# Inject flag at runtime if FLAG environment variable is set
if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > /tmp/flag
    echo "Flag injected to /tmp/flag"
else
    echo "Warning: FLAG environment variable not set"
fi

# Start Tomcat
exec catalina.sh run
