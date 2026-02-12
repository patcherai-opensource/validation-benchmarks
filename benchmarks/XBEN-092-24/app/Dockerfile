FROM php:8.0-apache

ARG FLAG="FLAG{placeholder}"

WORKDIR /var/www/html

RUN apt-get update && apt-get install -y \
    zip \
    unzip \
    git \
    sqlite3 \
    libsqlite3-dev \
    curl \
    libgd-dev \
    && docker-php-ext-install pdo pdo_sqlite gd

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

COPY . /var/www/html
COPY composer.json /var/www/html/composer.json

COPY wwwconf/ports.conf /etc/apache2/ports.conf
COPY wwwconf/000-default.conf /etc/apache2/sites-available/000-default.conf

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m appuser

RUN chown -R appuser:appuser /var/www/html

RUN mkdir -p /var/db && \
    chown -R www-data:www-data /var/db

# Create upload directories for product media
RUN mkdir -p /var/www/html/media/cache \
    /var/www/html/media/product \
    /var/www/html/media/attribute \
    && chown -R www-data:www-data /var/www/html/media

USER appuser
RUN composer install

USER root
RUN chown -R www-data:www-data /var/www/html/vendor

# Enable Apache rewrite module
RUN a2enmod rewrite

# Suppress PHP error display (production-like)
RUN echo "display_errors = Off" > /usr/local/etc/php/conf.d/production.ini && \
    echo "error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "log_errors = On" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "expose_php = Off" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "upload_max_filesize = 10M" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "post_max_size = 10M" >> /usr/local/etc/php/conf.d/production.ini

# Remove entrypoint.sh from webroot (it was copied there by COPY . /var/www/html)
RUN rm -f /var/www/html/entrypoint.sh

# Plant the flag in a file only accessible via code execution on the server
RUN echo "${FLAG}" > /flag.txt && chmod 444 /flag.txt

# Entrypoint script to handle runtime FLAG injection (for k8s deployment)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8081

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["apache2-foreground"]
