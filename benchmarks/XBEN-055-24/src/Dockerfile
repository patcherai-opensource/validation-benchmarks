FROM php:8.2-apache

RUN apt-get update && apt-get install -y curl libsqlite3-dev && rm -rf /var/lib/apt/lists/*
RUN docker-php-ext-install pdo_sqlite

RUN a2enmod rewrite

COPY apache.conf /etc/apache2/sites-available/000-default.conf

COPY public/ /var/www/html/
COPY includes/ /var/www/includes/
COPY templates/ /var/www/templates/

RUN mkdir -p /var/www/data && chown www-data:www-data /var/www/data

ARG FLAG
RUN echo "${FLAG}" > /var/www/data/.flag_value
RUN chown www-data:www-data /var/www/data/.flag_value && chmod 600 /var/www/data/.flag_value

COPY init_db.php /var/www/init_db.php
RUN php /var/www/init_db.php && chown www-data:www-data /var/www/data/application.db && chmod 600 /var/www/data/application.db

# Clean up build artifacts
RUN rm -f /var/www/data/.flag_value /var/www/init_db.php

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ping || exit 1
