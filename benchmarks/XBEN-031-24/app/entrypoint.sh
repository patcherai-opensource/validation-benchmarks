#!/bin/bash
set -e

# Write flag to /tmp/flag from environment variable
echo "${FLAG:-FLAG_PLACEHOLDER}" > /tmp/flag
chmod 644 /tmp/flag

# Execute the main command
exec "$@"
