#!/bin/bash

# Write flag to file from environment variable
if [ -n "$FLAG" ]; then
    echo "$FLAG" > /flag.txt
else
    echo "FLAG{placeholder}" > /flag.txt
fi

# Execute the original command
exec "$@"
