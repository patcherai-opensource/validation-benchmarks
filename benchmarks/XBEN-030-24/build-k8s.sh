#!/bin/bash

# Build script for Kubernetes deployment
set -e

# Get the flag from environment or generate one
FLAG=${FLAG:-"FLAG{placeholder_flag_for_k8s}"}

echo "Building containers for Kubernetes deployment..."
echo "Using FLAG: $FLAG"

# Build MySQL container
echo "Building MySQL container..."
docker build --platform linux/amd64 -t dolibarr-erp-mysql:latest ./mysql

# Build Web App container
echo "Building webapp container..."
docker build --platform linux/amd64 --build-arg FLAG="$FLAG" -t dolibarr-erp-webapp:latest ./wordpress

echo "Containers built successfully!"
echo "MySQL image: dolibarr-erp-mysql:latest"
echo "WebApp image: dolibarr-erp-webapp:latest"
echo ""
echo "To deploy to Kubernetes:"
echo "1. Tag and push images to your registry"
echo "2. Update XBEN-030-24.yaml with actual image names"
echo "3. Apply with: kubectl apply -f XBEN-030-24.yaml"
