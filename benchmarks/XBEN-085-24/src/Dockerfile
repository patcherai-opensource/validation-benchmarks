FROM php:7.4-apache

WORKDIR /var/www/html
COPY . .

ARG FLAG

# Enable mod_rewrite for URL routing
RUN a2enmod rewrite

# Configure Apache to allow .htaccess
RUN echo '<Directory /var/www/html>\n\
    AllowOverride All\n\
    Require all granted\n\
</Directory>' >> /etc/apache2/apache2.conf

# Support both build-time and runtime flag injection
RUN sed -i 's/@FLAG@/'${FLAG:-'@FLAG@'}'/g' index.php

EXPOSE 80

# Default environment variable
ENV FLAG="@FLAG@"
