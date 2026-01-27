FROM php:8.2-apache

RUN docker-php-ext-install mysqli

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

RUN mkdir /var/www/html/upload
RUN chown -R www-data:www-data /var/www/html

WORKDIR /var/www/html

# Add health check
HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
  CMD curl -f http://localhost/login.php || exit 1

EXPOSE 80
