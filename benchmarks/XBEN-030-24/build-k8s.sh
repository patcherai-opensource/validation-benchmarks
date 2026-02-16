#!/bin/bash

# Build script for Kubernetes deployment
set -e

# Get the flag from environment or generate one
FLAG=${FLAG:-"FLAG{placeholder_flag_for_k8s}"}

echo "Building containers for Kubernetes deployment..."
echo "Using FLAG: $FLAG"

# Build NetGate container
echo "Building NetGate container..."
docker build --build-arg FLAG="$FLAG" -t netgate-panel:latest ./wordpress

echo "Container built successfully!"
echo "NetGate image: netgate-panel:latest"
echo ""
echo "To deploy to Kubernetes:"
echo "1. Tag and push image to your registry"
echo "2. Update XBEN-030-24.yaml with actual image name"
echo "3. Replace PLACEHOLDER_FLAG with actual flag"
echo "4. Apply with: kubectl apply -f XBEN-030-24.yaml"
