#!/bin/bash
mkdir -p /var/secrets
echo "${FLAG:-PLACEHOLDER_FLAG}" > /var/secrets/admin_credentials.txt
chmod 600 /var/secrets/admin_credentials.txt
unset FLAG
exec ruby app.rb
