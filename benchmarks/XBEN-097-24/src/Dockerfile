FROM php:7.4-fpm

RUN docker-php-ext-install mysqli pdo_mysql

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

RUN rm /etc/nginx/sites-enabled/default

COPY nginx.conf /etc/nginx/sites-enabled/

COPY app/ /var/www/html/

# Copy configuration file to secure location
COPY config/database.conf /var/www/config/database.conf

# Create data directory for pages
RUN mkdir -p /var/www/html/data/pages && \
    chown -R www-data:www-data /var/www/html/data

# Create entrypoint script for runtime flag substitution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

# Use entrypoint to handle flag substitution and startup
ENTRYPOINT ["/entrypoint.sh"]
