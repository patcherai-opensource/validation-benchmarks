FROM php:7.4-apache

# Accept the flag as a build argument
ARG FLAG
ARG flag

RUN docker-php-ext-install mysqli

RUN a2enmod rewrite

RUN apt-get update && apt-get install -y default-mysql-client netcat-openbsd curl

RUN echo 'display_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'display_startup_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_reporting = E_ALL' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_log = /dev/stderr' >> /usr/local/etc/php/conf.d/errors.ini

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

# Replace @FLAG@ placeholder in db_init.sql with actual flag at build time
RUN sed -i "s|@FLAG@|${FLAG:-${flag:-FLAG{placeholder}}}|g" /app/db_init.sql

ENTRYPOINT ["/app/entrypoint.sh"]
