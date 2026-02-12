#!/bin/bash
set -e

# Create application configuration directory
mkdir -p /opt/spring-portal/app/data

# Write application configuration with flag
cat > /opt/spring-portal/app/data/application.properties << EOF
# Spring Application Properties
spring.application.name=portal
server.port=8080
spring.datasource.url=jdbc:mysql://localhost:3306/portal
spring.datasource.username=portal_user
spring.datasource.password=Ch4ng3M3!
app.secret.flag=${FLAG:-FLAG{default_flag_placeholder}}
logging.level.root=WARN
EOF

# Remove flag from environment to prevent leakage via /proc/self/environ
unset FLAG

# Start application server
exec gunicorn --bind 0.0.0.0:80 --workers 2 --access-logfile - run:application
