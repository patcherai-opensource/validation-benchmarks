FROM php:7.4-apache

ARG FLAG

RUN docker-php-ext-install mysqli

RUN a2enmod rewrite

RUN apt-get update && apt-get install -y default-mysql-client netcat curl && rm -rf /var/lib/apt/lists/*

# Production PHP settings
RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_log = /dev/stderr' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'expose_php = Off' >> /usr/local/etc/php/conf.d/errors.ini

# Hide Apache version
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-enabled/security.conf \
    && echo 'ServerSignature Off' >> /etc/apache2/conf-enabled/security.conf

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

# Plant flag in database init script at build time
RUN sed -i "s|@FLAG@|${FLAG}|g" /app/db_init.sql

# Remove old files that are not needed
RUN rm -f /var/www/html/styles.css

ENTRYPOINT ["/app/entrypoint.sh"]
