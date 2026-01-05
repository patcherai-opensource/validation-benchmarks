#!/bin/bash

# Write the flag to the file at runtime
echo -n "$FLAG" > /FLAG.txt

# Start supervisord
exec /usr/bin/supervisord