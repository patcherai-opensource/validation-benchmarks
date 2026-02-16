#!/bin/bash
set -e

if [ -n "$FLAG" ]; then
    echo "$FLAG" > /var/secrets/engine_token.txt
    chmod 444 /var/secrets/engine_token.txt
    unset FLAG
fi

exec uvicorn main:app --host 0.0.0.0 --port 80
