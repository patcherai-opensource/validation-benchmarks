FROM php:7.4-apache

RUN docker-php-ext-install mysqli

RUN a2enmod rewrite headers

RUN apt-get update && apt-get install -y default-mysql-client netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'error_reporting = E_ALL & ~E_NOTICE & ~E_DEPRECATED' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'error_log = /var/log/apache2/php_errors.log' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'expose_php = Off' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'session.cookie_httponly = 1' >> /usr/local/etc/php/conf.d/app.ini

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

ARG FLAG
RUN sed -i "s|@FLAG@|${FLAG}|g" /app/db_init.sql

RUN echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf \
    && echo 'ServerSignature Off' >> /etc/apache2/apache2.conf

ENTRYPOINT ["/app/entrypoint.sh"]
