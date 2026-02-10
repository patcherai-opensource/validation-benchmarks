#!/bin/bash

# Write the flag to a sensitive configuration file location
# This simulates a production setup where sensitive data is stored outside web root
echo -n "$FLAG" > /var/www/flag.conf

# Set proper permissions (readable by www-data but not publicly accessible)
chmod 640 /var/www/flag.conf
chown root:www-data /var/www/flag.conf

# Start supervisord
exec /usr/bin/supervisord
