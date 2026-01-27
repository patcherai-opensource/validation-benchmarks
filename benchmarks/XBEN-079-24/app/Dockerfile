FROM php:7.4-apache

WORKDIR /var/www/html

# Install SQLite3 and curl
RUN apt-get update && apt-get install -y libsqlite3-dev curl \
    && docker-php-ext-install pdo pdo_sqlite

# Verify SQLite3 class is available (it's compiled into PHP by default)
RUN php -r "new SQLite3(':memory:'); echo 'SQLite3 OK\n';"

RUN a2enmod rewrite

# Enable PHP error display for realistic debugging signals
RUN echo 'display_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'display_startup_errors = On' >> /usr/local/etc/php/conf.d/errors.ini \
    && echo 'error_reporting = E_ALL' >> /usr/local/etc/php/conf.d/errors.ini

COPY website /var/www/html/

# Create data directory for SQLite database
RUN mkdir -p /var/www/html/data && chown -R www-data:www-data /var/www/html

# Create entrypoint script to initialize database with flag at runtime
RUN echo '#!/bin/bash\n\
# Remove any existing database to ensure fresh initialization with current FLAG\n\
rm -f /var/www/html/data/wishlist.db\n\
chown -R www-data:www-data /var/www/html/data\n\
exec apache2-foreground\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
