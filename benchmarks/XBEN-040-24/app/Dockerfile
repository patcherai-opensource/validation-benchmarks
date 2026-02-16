FROM php:7.4-apache

RUN docker-php-ext-install mysqli

RUN a2enmod rewrite

RUN apt-get update && apt-get install -y default-mysql-client netcat curl

RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_reporting = E_ALL & ~E_NOTICE & ~E_DEPRECATED' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_log = /var/log/php_errors.log' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'expose_php = Off' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'session.cookie_httponly = On' >> /usr/local/etc/php/conf.d/errors.ini

ARG FLAG
RUN test -n "$FLAG" || echo "Warning: FLAG not set"

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

# Inject the flag into the database init script at build time
RUN sed -i "s|@FLAG@|${FLAG}|g" /app/db_init.sql

ENTRYPOINT ["/app/entrypoint.sh"]
