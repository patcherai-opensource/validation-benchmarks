#!/bin/bash

# Build script for Kubernetes deployment
set -e

# Get the flag from environment or generate one
FLAG=${FLAG:-"FLAG{placeholder_flag_for_k8s}"}

echo "Building containers for Kubernetes deployment..."
echo "Using FLAG: $FLAG"

# Build RaspAP container
echo "Building RaspAP container..."
docker build --build-arg FLAG="$FLAG" -t raspap-ctf:latest ./wordpress

echo "Container built successfully!"
echo "RaspAP image: raspap-ctf:latest"
