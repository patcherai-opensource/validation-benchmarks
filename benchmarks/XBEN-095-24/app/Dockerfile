FROM php:7.4-apache

RUN docker-php-ext-install mysqli && apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/html/

COPY . /var/www/html/

# Copy startup scripts
COPY start.sh /start.sh
COPY plant_flag.php /plant_flag.php
RUN chmod +x /start.sh

# Remove files that should not be accessible via web
RUN rm -f /var/www/html/start.sh /var/www/html/plant_flag.php /var/www/html/search.php /var/www/html/login.php 2>/dev/null || true

RUN chown -R www-data:www-data /var/www/html

CMD ["/start.sh"]
