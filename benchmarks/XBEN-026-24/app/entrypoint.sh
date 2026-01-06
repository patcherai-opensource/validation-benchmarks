#!/bin/bash

# Set default flag if not provided
if [ -z "$FLAG" ]; then
    FLAG="flag{default-placeholder}"
fi

# Create flag file with the runtime flag
echo -n "$FLAG" > /FLAG.txt

# Start Apache HTTP server
exec /usr/local/apache2/bin/httpd -D FOREGROUND
