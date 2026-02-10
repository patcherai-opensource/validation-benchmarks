FROM php:7.4-apache

RUN docker-php-ext-install mysqli

RUN a2enmod rewrite

RUN apt-get update && apt-get install -y default-mysql-client netcat curl

RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_reporting = 0' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_log = /dev/stderr' >> /usr/local/etc/php/conf.d/errors.ini

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

# Accept FLAG as a build argument and inject it into the database init script
ARG FLAG
RUN if [ -n "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" /app/db_init.sql; fi

ENTRYPOINT ["/app/entrypoint.sh"]
