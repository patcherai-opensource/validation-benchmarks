FROM php:8.3.6-apache

RUN apt-get update && apt-get install -y netcat-traditional curl && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install mysqli

# Enable Apache mod_rewrite
RUN a2enmod rewrite

COPY . /var/www/html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Configure PHP for production
RUN { \
    echo 'display_errors = Off'; \
    echo 'log_errors = On'; \
    echo 'error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT'; \
    echo 'expose_php = Off'; \
    echo 'session.cookie_httponly = 1'; \
} > /usr/local/etc/php/conf.d/production.ini

# Configure Apache
RUN { \
    echo 'ServerTokens Prod'; \
    echo 'ServerSignature Off'; \
} >> /etc/apache2/apache2.conf

# Set directory permissions for sessions
RUN mkdir -p /var/lib/php/sessions && chmod 1733 /var/lib/php/sessions

RUN chown -R www-data:www-data /var/www/html

ENTRYPOINT ["/entrypoint.sh"]
