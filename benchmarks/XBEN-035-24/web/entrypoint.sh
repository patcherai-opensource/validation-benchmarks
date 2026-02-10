#!/bin/bash
set -e

if [ ! -z "$FLAG" ]; then
    echo "$FLAG" > /tmp/flag
    chmod 600 /tmp/flag
fi

exec java -jar /app/app.jar
