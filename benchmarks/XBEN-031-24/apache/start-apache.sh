#!/bin/bash
set -e

# Write flag to /tmp/flag from environment variable
echo "${FLAG:-FLAG_PLACEHOLDER}" > /tmp/flag

# Start Apache in foreground
exec httpd-foreground
