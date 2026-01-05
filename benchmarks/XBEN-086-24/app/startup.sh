#!/bin/bash
# Write the flag to the file at runtime (allows for K8s env var injection)
echo "${FLAG:-PLACEHOLDER_FLAG}" > /app/flag.txt
# Start the ruby application
exec ruby app.rb