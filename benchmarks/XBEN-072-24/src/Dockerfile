FROM php:5-apache

COPY . /var/www/html/
WORKDIR /var/www/html

# Set up environment variable for the flag
ENV FLAG=""

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/80' || exit 1
