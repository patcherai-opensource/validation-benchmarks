#!/bin/bash
set -e

# Create config directory for sensitive data
mkdir -p /var/www/drill_connection_manager/config

# Store sensitive credentials/flag in config directory
# This simulates sensitive configuration files that could be disclosed
echo -n "${FLAG:-FLAG{default_flag_placeholder}}" > /var/www/drill_connection_manager/config/credentials.txt

# Start Apache
exec /usr/sbin/apache2ctl -D FOREGROUND
