#!/bin/bash
# Initialize data directory
mkdir -p /app/data

# If FLAG env var is set (k8s deployment), write it to credentials file
if [ -n "${FLAG}" ] && [ "${FLAG}" != "PLACEHOLDER_FLAG" ]; then
    echo "${FLAG}" > /opt/.credentials
    chmod 600 /opt/.credentials
fi

# Remove FLAG from environment to prevent disclosure
unset FLAG

# Start the application
exec ruby app.rb
