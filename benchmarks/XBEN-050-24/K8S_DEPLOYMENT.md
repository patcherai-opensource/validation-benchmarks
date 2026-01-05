# Kubernetes Deployment Guide for XBEN-050-24

## Overview
This CTF challenge has been migrated to support Kubernetes deployment while maintaining flag injection capabilities.

## Changes Made

### Application Code Changes
- Modified `src/app.py` to use configurable base URL via `BASE_URL` environment variable instead of hardcoded localhost
- Updated to support dynamic service discovery in Kubernetes

### Docker Configuration
- Enhanced `src/Dockerfile` to better support Kubernetes environment
- Added health check configuration for Kubernetes probes
- Proper environment variable handling for FLAG injection

### Kubernetes Manifest
- Created `k8s.yaml` with Deployment and Service configurations
- Single pod with web container running the Flask application
- Service exposes port 8080 externally, maps to container port 5000
- Resource limits and health checks configured
- Flag injection via environment variable `FLAG`

## Deployment

1. Build and push the Docker image:
   ```bash
   docker build -t <registry>/xben-050-24:latest src/
   docker push <registry>/xben-050-24:latest
   ```

2. Update the image reference in `k8s.yaml` from `/:-app` to your actual image

3. Set the FLAG environment variable in the deployment:
   ```bash
   kubectl apply -f k8s.yaml
   kubectl set env deployment/xben-050-24-web FLAG="FLAG{your-flag-here}"
   ```

## Environment Variables
- `FLAG`: The CTF flag to be injected (replaces @FLAG@ in secret.txt)
- `BASE_URL`: Base URL for the application (defaults to http://localhost:5000)
- `QT_QPA_PLATFORM`: Set to "offscreen" for PhantomJS
- `OPENSSL_CONF`: Set to "/dev/null" for SSL configuration

## Health Checks
The application includes both liveness and readiness probes that check TCP connectivity to port 5000.

## Access
The application will be available on port 8080 of the service, which maps to the container's port 5000.