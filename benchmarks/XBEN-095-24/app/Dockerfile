FROM php:7.4-apache

RUN docker-php-ext-install mysqli

WORKDIR /var/www/html/

COPY index.php uuid.php /var/www/html/

RUN chown -R www-data:www-data /var/www/html

CMD ["apache2-foreground"]
