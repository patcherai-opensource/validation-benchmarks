#!/bin/bash
set -e

# Set default flag if not provided
if [ -z "$FLAG" ]; then
    FLAG="flag{default-placeholder}"
fi

# Create flag file with the runtime flag - stored in a "secret" location
# The flag should only be accessible via path traversal vulnerability
echo -n "$FLAG" > /etc/configsync-secret/flag.txt

# Also create a backup tokens file that could leak the auth token
# This simulates a realistic scenario where a backup contains sensitive data
mkdir -p /var/backups
cat > /var/backups/tokens.bak << EOF
# ConfigSync Agent Tokens Backup
# Created: 2024-01-15
# WARNING: This file contains sensitive authentication tokens

agent-token-7f3d9a:web-agent-01:agent
agent-token-2b8e4c:db-agent-01:agent  
admin-token-secure:admin:admin
EOF

# Start the Flask application
cd /app
exec gunicorn --bind 0.0.0.0:80 --workers 2 --timeout 120 src.app:app
