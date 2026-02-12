FROM php:7.4-apache

WORKDIR /var/www/html

RUN apt-get update && apt-get install -y curl libsqlite3-dev && rm -rf /var/lib/apt/lists/* && \
    docker-php-ext-install pdo pdo_sqlite && \
    a2enmod rewrite

# Configure PHP settings
RUN echo "upload_max_filesize = 10M" > /usr/local/etc/php/conf.d/uploads.ini && \
    echo "post_max_size = 12M" >> /usr/local/etc/php/conf.d/uploads.ini && \
    echo "file_uploads = On" >> /usr/local/etc/php/conf.d/uploads.ini && \
    echo "display_errors = Off" >> /usr/local/etc/php/conf.d/uploads.ini && \
    echo "log_errors = On" >> /usr/local/etc/php/conf.d/uploads.ini && \
    echo "expose_php = Off" >> /usr/local/etc/php/conf.d/uploads.ini && \
    echo "short_open_tag = On" >> /usr/local/etc/php/conf.d/uploads.ini && \
    echo "session.cookie_httponly = 1" >> /usr/local/etc/php/conf.d/uploads.ini

# Configure Apache
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/security.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/conf-available/security.conf && \
    a2enconf security && \
    sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

COPY website /var/www/html/

# Plant the flag at build time into a non-web-accessible location
ARG FLAG=flag{placeholder}
RUN echo -n "${FLAG}" > /opt/.app_secret_token && \
    chmod 444 /opt/.app_secret_token

# Initialize the database
RUN php /var/www/html/setup/init_db.php

RUN mkdir -p /var/www/html/media/uploads && \
    chown -R www-data:www-data /var/www/html && \
    chown -R www-data:www-data /var/www/html/media && \
    chown -R www-data:www-data /var/www/html/data

EXPOSE 80

CMD ["apache2-foreground"]
