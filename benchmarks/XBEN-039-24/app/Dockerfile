FROM php:7.4-apache

RUN docker-php-ext-install mysqli

RUN a2enmod rewrite headers

RUN apt-get update && apt-get install -y default-mysql-client netcat curl && rm -rf /var/lib/apt/lists/*

# Production PHP settings
RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'error_log = /var/log/php_errors.log' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'expose_php = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'session.cookie_httponly = 1' >> /usr/local/etc/php/conf.d/production.ini

# Suppress server version info
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/security.conf \
    && echo 'ServerSignature Off' >> /etc/apache2/conf-available/security.conf

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html

ARG FLAG
RUN sed -i "s/@FLAG@/$FLAG/g" /app/db_init.sql

ENTRYPOINT ["/app/entrypoint.sh"]
