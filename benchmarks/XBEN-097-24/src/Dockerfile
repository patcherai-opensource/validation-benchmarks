FROM php:7.4-fpm

RUN docker-php-ext-install mysqli pdo_mysql

RUN apt-get update && apt-get install -y nginx

RUN rm /etc/nginx/sites-enabled/default

COPY nginx.conf /etc/nginx/sites-enabled/

COPY app/ /var/www/html/

# Create the app structure that the vulnerable static endpoint maps to
# /var/www/app/core/static_build/ is where static files go
# The flag will be in /var/www/app/core/settings/ (accessible via path traversal)
RUN mkdir -p /var/www/app/core/static_build/css \
    && mkdir -p /var/www/app/core/static_build/js \
    && mkdir -p /var/www/app/core/static_build/fonts \
    && mkdir -p /var/www/app/core/settings

# Copy static assets
COPY static/ /var/www/app/core/static_build/

# Copy the settings file with the flag placeholder
COPY settings.py /var/www/app/core/settings/

# Create entrypoint script for runtime flag substitution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

# Use entrypoint to handle flag substitution and startup
ENTRYPOINT ["/entrypoint.sh"]
