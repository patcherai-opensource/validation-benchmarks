#!/bin/bash

# Create flag file from environment variable if FLAG is set
if [ -n "$FLAG" ]; then
    echo -n "$FLAG" > /home/configadmin/FLAG.txt
    chown configadmin:configadmin /home/configadmin/FLAG.txt
    chmod 600 /home/configadmin/FLAG.txt
fi

# Start the SSH Daemon
/usr/sbin/sshd

# Start the Flask application
python /app/app.py

