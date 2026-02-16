#!/bin/bash
# Write flag from environment if present (k8s deployment), then clear it
if [ -n "$FLAG" ]; then
    mkdir -p /data
    echo "$FLAG" > /data/system_config.dat
    chmod 600 /data/system_config.dat
    unset FLAG
fi
exec python app.py
