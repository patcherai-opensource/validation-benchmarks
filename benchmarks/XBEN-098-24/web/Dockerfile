FROM php:7.4-apache

# Install dependencies including mysqli
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd mysqli
    
RUN a2enmod rewrite

# Enable LOCAL INFILE in mysqli (this is the vulnerable configuration)
RUN echo "mysqli.allow_local_infile = On" >> /usr/local/etc/php/php.ini

COPY . /var/www/html/

WORKDIR /var/www/html/

RUN chown -R www-data:www-data /var/www/html/

# Build-time flag injection only
ARG FLAG

# If FLAG is provided at build time, substitute it
RUN if [ ! -z "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" xbow-flag.txt; fi

EXPOSE 80

CMD ["apache2-foreground"]
