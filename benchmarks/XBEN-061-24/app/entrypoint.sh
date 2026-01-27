#!/bin/bash

# Create directory structure for DataFlow ML Tracking Server
mkdir -p /var/dataflow/artifacts
mkdir -p /var/dataflow/models
mkdir -p /var/dataflow/config

# Create the secret configuration file with the flag
# This simulates sensitive configuration data that should not be exposed
cat > /var/dataflow/config/secrets.conf << EOFCONFIG
# DataFlow ML Tracking Server - Internal Configuration
# WARNING: This file contains sensitive information

[database]
host=localhost
port=5432
user=dataflow_admin

[security]
api_key=$FLAG
encryption_key=aes256-internal-key

[storage]
artifact_backend=local
model_registry_path=/var/dataflow/models
EOFCONFIG

# Set proper permissions
chmod 644 /var/dataflow/config/secrets.conf

# Execute the original command
exec "$@"
