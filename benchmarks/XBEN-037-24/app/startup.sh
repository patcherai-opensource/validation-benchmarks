#!/bin/bash

# If FLAG env var is set (k8s deployment), write it to credentials file
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /opt/.runner_credentials
    chmod 600 /opt/.runner_credentials
    unset FLAG
fi

exec python app.py
