#!/bin/bash

# Build script for Kubernetes deployment
set -e

# Get the flag from environment or generate one
FLAG=${FLAG:-"FLAG{placeholder_flag_for_k8s}"}

echo "Building containers for Kubernetes deployment..."
echo "Using FLAG: $FLAG"

# Build MySQL container
echo "Building MySQL container..."
docker build -t wordpress-ctf-mysql:latest ./mysql

# Build WordPress container
echo "Building WordPress container..."
docker build --build-arg FLAG="$FLAG" -t wordpress-ctf-app:latest ./wordpress

echo "Containers built successfully!"
echo "MySQL image: wordpress-ctf-mysql:latest"
echo "WordPress image: wordpress-ctf-app:latest"
echo ""
echo "To deploy to Kubernetes:"
echo "1. Tag and push images to your registry"
echo "2. Update k8s.yaml with actual image names"
echo "3. Replace PLACEHOLDER_FLAG with actual flag"
echo "4. Apply with: kubectl apply -f k8s.yaml"