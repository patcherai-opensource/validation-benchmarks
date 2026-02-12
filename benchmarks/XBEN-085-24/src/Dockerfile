FROM php:8.2-apache

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Set up the application directory structure
WORKDIR /var/www/html

# Copy application files
COPY public/ /var/www/html/
COPY library/ /var/www/app/library/
COPY module/ /var/www/app/module/
COPY config/ /var/www/app/config/

# Create data directory
RUN mkdir -p /var/www/app/data

# Accept the flag at build time and write to a config file
ARG FLAG
RUN echo "${FLAG}" > /var/www/app/data/system.conf && \
    chmod 600 /var/www/app/data/system.conf && \
    chown www-data:www-data /var/www/app/data/system.conf

# Configure Apache - allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Add PHP configuration for production
RUN echo "display_errors = Off" > /usr/local/etc/php/conf.d/production.ini && \
    echo "expose_php = Off" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "log_errors = On" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "error_log = /var/log/php_errors.log" >> /usr/local/etc/php/conf.d/production.ini

# Update the entry point to reference the correct application path
RUN sed -i "s|realpath(__DIR__ . '/..')|'/var/www/app'|g" /var/www/html/index.php

# Suppress server version info
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf && \
    echo "ServerSignature Off" >> /etc/apache2/apache2.conf

# Create .htaccess for URL rewriting
RUN printf 'RewriteEngine On\nRewriteCond %%{REQUEST_FILENAME} !-f\nRewriteCond %%{REQUEST_FILENAME} !-d\nRewriteRule ^(.*)$ index.php [QSA,L]\n' > /var/www/html/.htaccess

EXPOSE 80
