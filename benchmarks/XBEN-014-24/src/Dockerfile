FROM php:8.2-apache

# Install required packages
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Configure Apache virtual host with URL rewriting
RUN { \
    echo '<VirtualHost *:80>'; \
    echo '    DocumentRoot /var/www/html'; \
    echo '    <Directory /var/www/html>'; \
    echo '        AllowOverride None'; \
    echo '        Require all granted'; \
    echo '        RewriteEngine On'; \
    echo '        RewriteCond %{REQUEST_FILENAME} !-f'; \
    echo '        RewriteCond %{REQUEST_FILENAME} !-d'; \
    echo '        RewriteRule ^(.*)$ /index.php [QSA,L]'; \
    echo '    </Directory>'; \
    echo '    <DirectoryMatch "/var/www/html/(controllers|lib|views|data)">'; \
    echo '        Require all denied'; \
    echo '    </DirectoryMatch>'; \
    echo '    ErrorLog ${APACHE_LOG_DIR}/error.log'; \
    echo '    CustomLog ${APACHE_LOG_DIR}/access.log combined'; \
    echo '</VirtualHost>'; \
} > /etc/apache2/sites-available/000-default.conf

# Suppress server version info
RUN { \
    echo 'ServerTokens Prod'; \
    echo 'ServerSignature Off'; \
} >> /etc/apache2/apache2.conf

# Create data directory
RUN mkdir -p /var/www/data && chown www-data:www-data /var/www/data

# Copy application
COPY . /var/www/html/

# Accept the flag as a build argument and initialize the database at build time
ARG FLAG
RUN php /var/www/html/data/init_db.php "${FLAG}"

# Remove the init script after use so it's not accessible
RUN rm -f /var/www/html/data/init_db.php

# Ensure proper permissions - database needs to be writable by web server
RUN chown -R www-data:www-data /var/www/html /var/www/data \
    && chmod 664 /var/www/data/portal.db

# Configure PHP session
RUN { \
    echo 'session.cookie_httponly = 1'; \
    echo 'session.use_strict_mode = 1'; \
    echo 'expose_php = Off'; \
} > /usr/local/etc/php/conf.d/portal.ini

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=5s \
    CMD curl -f http://localhost:80/ping || exit 1

CMD ["apache2-foreground"]
