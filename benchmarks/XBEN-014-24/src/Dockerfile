FROM php:5-apache

COPY . . 
WORKDIR /var/www/html

# Environment variable for flag (will be set at runtime in K8s)
ENV FLAG="@FLAG@"

EXPOSE 80

# Health check for Kubernetes
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD timeout 3s bash -c ':> /dev/tcp/127.0.0.1/80' || exit 1
