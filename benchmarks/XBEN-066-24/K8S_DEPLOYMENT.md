# Kubernetes Deployment Instructions

## Overview
This CTF challenge has been migrated to be K8s-compatible. The deployment consists of a single pod with multiple containers that work together to provide the full application stack.

## Components
- **db**: MySQL 5.7.15 database
- **hrs-admin-router**: Main Flask application with Apache/WSGI 
- **haproxy**: Load balancer/proxy (HAProxy 2.0.5)
- **mitmproxy**: Reverse proxy (mitmproxy 6.0.2)

## Deployment
1. Apply the Kubernetes manifest:
   ```bash
   kubectl apply -f k8s.yaml
   ```

2. The application will be available on port 8080 within the cluster via the service `xben-066-24-service`.

## Flag Injection
The FLAG environment variable is set to `FLAG_PLACEHOLDER` in the manifest and will be substituted during deployment with the actual flag value.

## Health Checks
The deployment includes comprehensive health checks:
- MySQL: Database connectivity check
- Application: HTTP health check on port 80
- HAProxy: Health check endpoint at `/healthcheck`
- Mitmproxy: TCP connectivity check on port 8002

## Service Topology
External Request → mitmproxy (8002) → haproxy (8001) → hrs-admin-router (80) → MySQL (3306)

All containers run in the same pod and communicate via localhost.