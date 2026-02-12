FROM php:8.2-apache

RUN apt-get update && \
    apt-get install -y curl && \
    docker-php-ext-install pdo pdo_mysql && \
    rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Configure Apache to suppress server tokens and allow htaccess
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security.conf && \
    echo "ServerSignature Off" >> /etc/apache2/conf-available/security.conf && \
    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Copy application files
COPY index.php /var/www/html/index.php
COPY dashboard.php /var/www/html/dashboard.php
COPY pages.php /var/www/html/pages.php
COPY content.php /var/www/html/content.php
COPY settings.php /var/www/html/settings.php
COPY users.php /var/www/html/users.php
COPY classes/ /var/www/html/classes/
COPY config/ /var/www/html/config/
COPY static/ /var/www/html/static/

# Remove default Apache index
RUN rm -f /var/www/html/index.html

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html

COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

WORKDIR /var/www/html

EXPOSE 80

CMD ["/usr/local/bin/start.sh"]
