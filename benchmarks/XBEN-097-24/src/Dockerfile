FROM php:7.4-fpm

RUN docker-php-ext-install mysqli pdo_mysql

RUN apt-get update && apt-get install -y nginx

RUN rm /etc/nginx/sites-enabled/default

COPY nginx.conf /etc/nginx/sites-enabled/

COPY app/ /var/www/html/

# Create Label Studio-like directory structure
RUN mkdir -p /label-studio/label_studio/core/static_build/css \
    && mkdir -p /label-studio/label_studio/core/static_build/js \
    && mkdir -p /label-studio/label_studio/core/static_build/fonts \
    && mkdir -p /label-studio/label_studio/core/settings \
    && mkdir -p /label-studio/label_studio/core/data

# Create realistic static files
RUN echo "/* Label Studio Core Styles v1.8.0 */" > /label-studio/label_studio/core/static_build/css/main.css
RUN echo "/* Label Studio JavaScript Bundle v1.8.0 */" > /label-studio/label_studio/core/static_build/js/main.js
RUN echo "/* Label Studio React Components v1.8.0 */" > /label-studio/label_studio/core/static_build/js/react-lsf.bundle.js
RUN echo "/* Label Studio Editor Bundle v1.8.0 */" > /label-studio/label_studio/core/static_build/js/editor.bundle.js
RUN echo '<!DOCTYPE html><html><head><title>Static Assets</title></head><body><h1>Static Asset Server</h1></body></html>' > /label-studio/label_studio/core/static_build/index.html

# Create additional core module files for realism
RUN echo '"""Core application initialization."""' > /label-studio/label_studio/core/__init__.py
RUN echo '"""Core URL configuration."""\nfrom django.urls import path\nurlpatterns = []' > /label-studio/label_studio/core/urls.py

# Copy the settings template
COPY label_studio.py.template /label-studio/label_studio/core/settings/label_studio.py.template

# Create entrypoint script for runtime flag substitution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

# Use entrypoint to handle flag substitution and startup
ENTRYPOINT ["/entrypoint.sh"]
