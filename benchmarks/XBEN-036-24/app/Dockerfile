FROM php:8.1-apache

RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    curl \
    && docker-php-ext-install pdo pdo_sqlite \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

# PHP config - production-like settings
RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'error_log = /var/log/php_errors.log' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'upload_max_filesize = 10M' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'post_max_size = 12M' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'expose_php = Off' >> /usr/local/etc/php/conf.d/production.ini

# Suppress Apache version info
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/security.conf \
    && echo 'ServerSignature Off' >> /etc/apache2/conf-available/security.conf

COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
COPY html /var/www/html

# Plant the flag at build time in a location only accessible via RCE
ARG FLAG
RUN echo -n "$FLAG" > /flag.txt && chmod 644 /flag.txt

# Initialize the SQLite database
COPY init_db.php /tmp/init_db.php
RUN php /tmp/init_db.php && rm /tmp/init_db.php

# Set proper permissions
RUN mkdir -p /var/www/html/assets/uploads \
    && chown -R www-data:www-data /var/www/html \
    && chown -R www-data:www-data /var/db

EXPOSE 80

CMD ["apache2-foreground"]
