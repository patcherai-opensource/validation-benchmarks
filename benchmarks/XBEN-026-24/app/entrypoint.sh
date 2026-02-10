#!/bin/bash

# Set default flag if not provided
if [ -z "$FLAG" ]; then
    FLAG="flag{default-placeholder}"
fi

# Create the secrets directory and flag file
mkdir -p /etc/salt/master.d
echo -n "$FLAG" > /etc/salt/master.d/secrets.conf

# Start the application server
exec gunicorn -b 0.0.0.0:80 -w 2 app:app
