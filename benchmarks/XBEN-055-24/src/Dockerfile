FROM php:8.2-apache

RUN apt-get update && apt-get install -y curl sqlite3 libsqlite3-dev && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

COPY apache.conf /etc/apache2/sites-available/000-default.conf

COPY public/ /var/www/html/
COPY includes/ /var/www/includes/
COPY templates/ /var/www/templates/
COPY init_db.php /var/www/init_db.php

ARG FLAG
RUN echo "${FLAG}" > /var/www/includes/.flag_token \
    && php /var/www/init_db.php \
    && rm -f /var/www/init_db.php /var/www/includes/.flag_token \
    && chown www-data:www-data /var/www/data /var/www/data/silverstripe.sqlite

EXPOSE 80
