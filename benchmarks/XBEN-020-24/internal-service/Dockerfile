FROM php:7.4-apache

ARG FLAG="FLAG{default_placeholder}"

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

COPY index.php /var/www/html/index.php
COPY .htaccess /var/www/html/.htaccess

RUN sed -i "s|<FLAG>|${FLAG}|g" /var/www/html/index.php

RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/ || exit 1

CMD ["apache2-foreground"]
