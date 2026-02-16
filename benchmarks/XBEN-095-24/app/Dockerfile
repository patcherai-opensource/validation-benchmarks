FROM php:7.4-apache

RUN docker-php-ext-install mysqli && a2enmod rewrite headers

WORKDIR /var/www/html/

COPY . /var/www/html/

COPY apache-vhost.conf /etc/apache2/sites-available/000-default.conf

RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html

CMD ["apache2-foreground"]
