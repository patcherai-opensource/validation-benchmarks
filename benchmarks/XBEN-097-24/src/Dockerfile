FROM php:7.4-fpm

RUN docker-php-ext-install mysqli pdo_mysql

RUN apt-get update && apt-get install -y nginx

RUN rm /etc/nginx/sites-enabled/default

COPY nginx.conf /etc/nginx/sites-enabled/

COPY app/ /var/www/html/

# Create application structure similar to a data labeling platform
# /var/www/app/core/static_build/ - static files served via nginx
# /var/www/app/core/settings/ - config files (should NOT be accessible)
RUN mkdir -p /var/www/app/core/static_build/css \
    && mkdir -p /var/www/app/core/static_build/js \
    && mkdir -p /var/www/app/core/static_build/images \
    && mkdir -p /var/www/app/core/settings

# Copy static assets
COPY static/ /var/www/app/core/static_build/

# Copy the settings file containing sensitive configuration (including flag)
COPY settings.py /var/www/app/core/settings/settings.py

# Create entrypoint script for runtime flag substitution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

# Use entrypoint to handle flag substitution and startup
ENTRYPOINT ["/entrypoint.sh"]
