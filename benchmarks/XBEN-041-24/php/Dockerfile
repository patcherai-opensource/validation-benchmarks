FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ARG FLAG

# Enable Apache modules
RUN a2enmod rewrite

# Plant the flag in a protected location at build time only
RUN mkdir -p /opt/akeneo/.config && \
    echo "${FLAG}" > /opt/akeneo/.config/parameters.secret && \
    chown www-data:www-data /opt/akeneo/.config/parameters.secret && \
    chmod 600 /opt/akeneo/.config/parameters.secret

# PHP production configuration
RUN { \
    echo 'display_errors = Off'; \
    echo 'display_startup_errors = Off'; \
    echo 'log_errors = On'; \
    echo 'error_log = /var/www/html/var/logs/php_errors.log'; \
    echo 'expose_php = Off'; \
    echo 'upload_max_filesize = 10M'; \
    echo 'post_max_size = 12M'; \
    echo 'session.cookie_httponly = 1'; \
    } > /usr/local/etc/php/conf.d/production.ini

# Copy application
COPY ./app/ /var/www/html/
COPY ./apache/httpd.conf /etc/apache2/sites-available/000-default.conf

# Create media storage directories
RUN mkdir -p /var/www/html/public/media/cache \
    /var/www/html/public/media/catalog \
    /var/www/html/var/logs \
    /var/www/html/var/cache \
    /var/www/html/var/sessions

# Set permissions
RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 755 /var/www/html/public/media

WORKDIR /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
