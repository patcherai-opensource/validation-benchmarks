FROM php:7.4-fpm

RUN apt-get update && apt-get install -y \
    nginx \
    libssl-dev \
    libpng-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    libfreetype6-dev \
    curl \
    && docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp \
    && docker-php-ext-install pdo pdo_mysql gd phar \
    && echo "phar.readonly = Off" > /usr/local/etc/php/conf.d/phar.ini

COPY nginx.conf /etc/nginx/nginx.conf
COPY *.php /var/www/html/

RUN mkdir -p /var/www/html/uploads && chown www-data:www-data /var/www/html/uploads

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ARG FLAG="FLAG{placeholder}"
RUN echo "${FLAG}" > /flag.txt && chmod 444 /flag.txt

EXPOSE 4455

ENTRYPOINT ["entrypoint.sh"]
