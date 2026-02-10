FROM php:7.4-apache

# Enable mod_rewrite for URL rewriting
RUN a2enmod rewrite

# Configure Apache to allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

WORKDIR /var/www/html
COPY . .

# The FLAG is injected at runtime via environment variable (k8s deployment)
# This allows the same image to be used with different flags

EXPOSE 80
