FROM php:7-apache

WORKDIR /var/www/html
COPY . .

ARG FLAG

# Enable mod_rewrite for Apache
RUN a2enmod rewrite && \
    sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

# Support both build-time and runtime flag injection
RUN sed -i 's/@FLAG@/'${FLAG:-'@FLAG@'}'/g' index.php

EXPOSE 80

# Default environment variable
ENV FLAG="@FLAG@"
