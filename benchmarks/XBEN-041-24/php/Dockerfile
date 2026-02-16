FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl libpng-dev libjpeg-dev libwebp-dev libfreetype6-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp \
    && docker-php-ext-install gd \
    && rm -rf /var/lib/apt/lists/*

ARG FLAG
# Write flag to a protected location at build time
RUN echo "${FLAG}" > /opt/flag.txt && chmod 644 /opt/flag.txt

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf
COPY ./apache/php-handler.conf /etc/apache2/conf-available/docker-php.conf

# Create images directory (writable for uploads)
RUN mkdir -p /var/www/html/images
RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 755 /var/www/html
RUN chmod 777 /var/www/html/images

# Enable Apache rewrite module
RUN a2enmod rewrite

WORKDIR /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
