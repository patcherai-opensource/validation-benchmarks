FROM php:8.3.6-apache

RUN apt-get update && apt-get install -y netcat-traditional curl

# Enable Apache modules
RUN a2enmod rewrite

# Configure Apache to allow .htaccess
RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

COPY . /var/www/html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN docker-php-ext-install mysqli
RUN chown -R www-data:www-data /var/www/html

ENTRYPOINT ["/entrypoint.sh"]
