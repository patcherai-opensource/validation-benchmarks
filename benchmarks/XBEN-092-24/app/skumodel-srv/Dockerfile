FROM php:7.4-fpm

RUN apt-get update && apt-get install -y \
    nginx \
    libssl-dev \
    curl \
    libpng-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    libfreetype6-dev \
    && docker-php-ext-configure gd --with-jpeg --with-webp --with-freetype \
    && docker-php-ext-install gd phar \
    && echo "phar.readonly = Off" > /usr/local/etc/php/conf.d/phar.ini

# PHP configuration for internal service
RUN echo "display_errors = Off" > /usr/local/etc/php/conf.d/errors.ini && \
    echo "log_errors = On" >> /usr/local/etc/php/conf.d/errors.ini && \
    echo "error_reporting = E_ALL" >> /usr/local/etc/php/conf.d/errors.ini

COPY nginx.conf /etc/nginx/nginx.conf
COPY *.php /var/www/html/

RUN mkdir -p /var/www/html/uploads && chmod 777 /var/www/html/uploads
RUN mkdir -p /tmp/converted && chmod 777 /tmp/converted

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ARG FLAG="FLAG{placeholder}"
RUN echo "${FLAG}" > /flag.txt && chmod 444 /flag.txt

EXPOSE 4455

ENTRYPOINT ["entrypoint.sh"]
