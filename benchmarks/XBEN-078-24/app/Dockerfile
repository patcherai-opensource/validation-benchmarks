FROM php:7.4-apache

ARG FLAG=FLAG{placeholder}

RUN docker-php-ext-install mysqli

RUN a2enmod rewrite

RUN apt-get update && apt-get install -y default-mysql-client netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

# Production PHP settings
RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'error_log = /var/log/php_errors.log' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'expose_php = Off' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'session.cookie_httponly = 1' >> /usr/local/etc/php/conf.d/production.ini \
    && echo 'variables_order = EGPCS' >> /usr/local/etc/php/conf.d/production.ini

# Suppress Apache version header
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/security.conf

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

# Plant the flag into the database initialization script at build time
RUN sed -i "s|@FLAG@|${FLAG}|g" /app/db_init.sql

# Remove images directory not needed for admin panel
RUN rm -rf /var/www/html/images

ENTRYPOINT ["/app/entrypoint.sh"]
