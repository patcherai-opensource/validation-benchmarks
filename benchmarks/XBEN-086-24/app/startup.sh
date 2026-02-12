#!/bin/bash
# If FLAG is set as runtime env var (k8s deployment), update the api_key file
if [ -n "$FLAG" ] && [ "$FLAG" != "PLACEHOLDER_FLAG" ]; then
    echo "$FLAG" > /etc/lollms/api_key
fi
# Unset the env var so it's not accessible via /proc/self/environ
unset FLAG
exec python app.py
