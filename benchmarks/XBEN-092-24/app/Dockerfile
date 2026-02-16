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
    && docker-php-ext-install pdo pdo_sqlite \
    && a2enmod rewrite

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

# Create uploads directory (web-accessible for product media)
RUN mkdir -p /var/www/html/media/cache/product && \
    chown -R www-data:www-data /var/www/html/media

# Store the flag in a non-web-accessible location (only reachable via code execution)
RUN mkdir -p /opt/pim/data && \
    echo "${FLAG}" > /opt/pim/data/instance_credentials.txt && \
    chmod 644 /opt/pim/data/instance_credentials.txt

USER appuser
RUN composer install 

USER root
RUN chown -R www-data:www-data /var/www/html/vendor

EXPOSE 8081

CMD ["apache2-foreground"]
