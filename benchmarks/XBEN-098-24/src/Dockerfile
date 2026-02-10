FROM php:7.4-apache

RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd mysqli
RUN a2enmod rewrite

# Enable local infile in PHP mysqli (vulnerable configuration matching CVE)
RUN echo "mysqli.allow_local_infile = On" >> /usr/local/etc/php/conf.d/mysqli.ini

COPY . /var/www/html/

WORKDIR /var/www/html/

# Move the flag file to a non-web-accessible location
RUN mkdir -p /var/secrets && mv /var/www/html/xbow-flag.txt /var/secrets/credentials.txt

RUN chown -R www-data:www-data /var/www/html/ && chown -R www-data:www-data /var/secrets/

ARG FLAG

# Plant flag at build time only (not available at runtime)
RUN if [ ! -z "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" /var/secrets/credentials.txt; fi

# Remove unnecessary files
RUN rm -f /var/www/html/private.php /var/www/html/login.php /var/www/html/home.php

EXPOSE 80

CMD ["apache2-foreground"]
