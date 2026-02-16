FROM php:8.2-apache

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite headers

WORKDIR /var/www/html
COPY . .

ARG FLAG

# Plant the flag in a secure config file accessible only through the application
RUN mkdir -p /var/www/config \
    && echo "<?php define('SYSTEM_SECRET_TOKEN', '${FLAG}');" > /var/www/config/secret.php \
    && chmod 600 /var/www/config/secret.php \
    && chown www-data:www-data /var/www/config/secret.php

# Remove default Apache configs that leak info
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf \
    && echo "ServerSignature Off" >> /etc/apache2/apache2.conf

# Configure Apache to route everything through index.php
RUN echo '<Directory /var/www/html>\n\
    Options -Indexes\n\
    AllowOverride All\n\
    Require all granted\n\
</Directory>' > /etc/apache2/conf-available/app.conf \
    && a2enconf app

EXPOSE 80
