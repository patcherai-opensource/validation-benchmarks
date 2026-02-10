FROM php:7.4-apache

RUN docker-php-ext-install mysqli

RUN { \
    echo 'display_errors = Off'; \
    echo 'log_errors = On'; \
    echo 'expose_php = Off'; \
} > /usr/local/etc/php/conf.d/production.ini

WORKDIR /var/www/html/

COPY . /var/www/html/

RUN chown -R www-data:www-data /var/www/html

CMD ["apache2-foreground"]
