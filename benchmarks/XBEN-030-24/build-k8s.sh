#!/bin/bash

# Build script for Kubernetes deployment
set -e

# Get the flag from environment or generate one
FLAG=${FLAG:-"FLAG{placeholder_flag_for_k8s}"}

echo "Building containers for Kubernetes deployment..."
echo "Using FLAG: $FLAG"

# Build app container
echo "Building app container..."
docker build --build-arg FLAG="$FLAG" -t pluginmanager-ctf-app:latest ./app

echo "Containers built successfully!"
echo "App image: pluginmanager-ctf-app:latest"
echo ""
echo "To deploy to Kubernetes:"
echo "1. Tag and push images to your registry"
echo "2. Update XBEN-030-24.yaml with actual image names"
echo "3. Apply with: kubectl apply -f XBEN-030-24.yaml"
