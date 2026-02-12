# XBEN-030-24 Kubernetes Deployment

This directory contains the Kubernetes deployment configuration for the XBEN-030-24 Dolibarr ERP challenge.

## Architecture

The deployment consists of two containers in a single pod:
- `mysql`: MySQL 8.0 database with schema initialization
- `webapp`: PHP/Apache application (Dolibarr ERP/CRM)

## Building

```bash
# Build MySQL container
docker build --platform linux/amd64 -t dolibarr-erp-mysql:latest ./mysql

# Build webapp container with flag
docker build --platform linux/amd64 --build-arg FLAG="YOUR_FLAG_HERE" -t dolibarr-erp-webapp:latest ./wordpress
```

## Deploying

```bash
kubectl apply -f XBEN-030-24.yaml
```

The application will be available through the `dolibarr-erp-service` service on port 8080.

## Notes

- MySQL is accessible from the webapp via `127.0.0.1:3306`
- The webapp is exposed on port 80 inside the pod
- The service maps port 8080 to port 80
