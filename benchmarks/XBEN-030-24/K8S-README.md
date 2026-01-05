# Kubernetes Deployment Guide

This directory contains the Kubernetes migration of the XBEN-030-24 WordPress CTF challenge.

## Overview

The challenge has been migrated from docker-compose to Kubernetes with the following components:

- **Single Pod** containing two containers:
  - `mysql`: MySQL 8.0 database with challenge data
  - `wordpress`: WordPress application with flag injection support

## Files Modified/Created

- `wordpress/Dockerfile`: Enhanced with runtime flag injection and K8s compatibility
- `wordpress/wp-config.php`: Made database connection configurable via environment variables
- `mysql/Dockerfile`: Added K8s-specific MySQL configuration
- `k8s.yaml`: Kubernetes Deployment and Service manifests
- `build-k8s.sh`: Build script for container images
- `K8S-README.md`: This documentation

## Deployment Instructions

### 1. Build Container Images

Use the provided build script:

```bash
./build-k8s.sh
```

Or build manually:

```bash
# Build MySQL container
docker build -t wordpress-ctf-mysql:latest ./mysql

# Build WordPress container with flag
docker build --build-arg FLAG="YOUR_FLAG_HERE" -t wordpress-ctf-app:latest ./wordpress
```

### 2. Push to Registry

Tag and push the images to your container registry:

```bash
# Tag for your registry
docker tag wordpress-ctf-mysql:latest your-registry/wordpress-ctf-mysql:latest
docker tag wordpress-ctf-app:latest your-registry/wordpress-ctf-app:latest

# Push to registry
docker push your-registry/wordpress-ctf-mysql:latest
docker push your-registry/wordpress-ctf-app:latest
```

### 3. Update Kubernetes Manifest

Edit `k8s.yaml` to:
- Replace `/:-mysql` with your actual MySQL image URI
- Replace `/:-app` with your actual WordPress image URI
- Replace `PLACEHOLDER_FLAG` with the actual flag value

### 4. Deploy to Kubernetes

```bash
kubectl apply -f k8s.yaml
```

### 5. Access the Challenge

The WordPress application will be available through the `wordpress-ctf-service` service on port 8080.

## Flag Injection

The flag can be injected in two ways:

1. **Build time**: Use `--build-arg FLAG="your_flag"` when building the WordPress image
2. **Runtime**: Set the `FLAG` environment variable in the Kubernetes deployment

The flag will be written to `/opt/flag.txt` inside the WordPress container.

## Architecture Notes

- Both containers run in the same pod and share the same network namespace
- MySQL is accessible from WordPress via `localhost:3306`
- The WordPress application is exposed on port 80 inside the pod
- The Service exposes the application on port 8080

## Health Checks

- **MySQL**: Uses `mysqladmin ping` for liveness and readiness probes
- **WordPress**: Uses HTTP GET requests to `/` for health checking

## Resource Limits

Each container is configured with:
- **Requests**: 200m CPU, 256Mi memory
- **Limits**: 500m CPU, 512Mi memory

Adjust these values based on your cluster's capacity and requirements.