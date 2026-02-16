#!/bin/bash

# Build script for Kubernetes deployment
set -e

# Get the flag from environment or generate one
FLAG=${FLAG:-"FLAG{placeholder_flag_for_k8s}"}

echo "Building containers for Kubernetes deployment..."
echo "Using FLAG: $FLAG"

# Build MySQL container
echo "Building MySQL container..."
docker build --platform linux/amd64 -t gestipro-erp-mysql:latest ./mysql

# Build GestiPro container
echo "Building GestiPro container..."
docker build --platform linux/amd64 --build-arg FLAG="$FLAG" -t gestipro-erp-app:latest ./app

echo "Containers built successfully!"
echo "MySQL image: gestipro-erp-mysql:latest"
echo "GestiPro image: gestipro-erp-app:latest"
