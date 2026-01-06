FROM php:7.4-apache

COPY . /var/www/html/

RUN apt-get update -y

RUN apt-get install -y curl libcurl4-openssl-dev pkg-config

RUN docker-php-ext-install curl

EXPOSE 80

# Health check for Kubernetes
HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/ || exit 1
