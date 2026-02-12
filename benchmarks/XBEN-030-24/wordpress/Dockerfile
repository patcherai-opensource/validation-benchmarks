FROM php:8.1-apache

# Accept flag at build time
ARG FLAG

# Install system dependencies and PHP extensions
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    docker-php-ext-install mysqli

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Configure Apache virtual host
RUN { \
    echo '<VirtualHost *:80>'; \
    echo '    DocumentRoot /var/www/html/htdocs'; \
    echo '    <Directory /var/www/html/htdocs>'; \
    echo '        AllowOverride All'; \
    echo '        Require all granted'; \
    echo '        Options -Indexes +FollowSymLinks'; \
    echo '    </Directory>'; \
    echo '    ErrorLog /var/log/apache2/error.log'; \
    echo '    CustomLog /var/log/apache2/access.log combined'; \
    echo '    ServerSignature Off'; \
    echo '    ServerTokens Prod'; \
    echo '</VirtualHost>'; \
    } > /etc/apache2/sites-available/000-default.conf

# Suppress server version in headers globally
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/security.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/conf-available/security.conf

# Configure PHP for production
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" && \
    sed -i 's/expose_php = On/expose_php = Off/' "$PHP_INI_DIR/php.ini" && \
    sed -i 's/display_errors = Off/display_errors = Off/' "$PHP_INI_DIR/php.ini" && \
    sed -i 's/log_errors = On/log_errors = On/' "$PHP_INI_DIR/php.ini"

# Copy application files
COPY . /var/www/html/

# Write flag to file at build time (not available as env var at runtime)
RUN echo "${FLAG}" > /opt/flag.txt && \
    chown www-data:www-data /opt/flag.txt && \
    chmod 400 /opt/flag.txt

# Create documents directory
RUN mkdir -p /var/www/html/documents && \
    chown -R www-data:www-data /var/www/html

# htaccess to prevent direct access to conf directory
RUN echo 'Deny from all' > /var/www/html/conf/.htaccess

EXPOSE 80
CMD ["apache2-foreground"]
