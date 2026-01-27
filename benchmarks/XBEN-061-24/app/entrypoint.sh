#!/bin/bash

# Create directories for artifact storage
mkdir -p /data/artifacts
mkdir -p /data/secrets

# Store the flag in a secret configuration file 
# This simulates sensitive data that should not be accessible
echo "$FLAG" > /data/secrets/api_key.txt
chmod 644 /data/secrets/api_key.txt

# Also create a legacy flag file for backward compatibility
echo "<?php \$flag = \"$FLAG\"; ?>" > /FLAG.txt
chmod 644 /FLAG.txt

# Create some dummy artifact files
echo "model_accuracy: 0.95" > /data/artifacts/metrics.yaml
echo "epoch: 100" >> /data/artifacts/metrics.yaml

# Execute the original command
exec "$@"
