FROM php:8.1-apache

# Install system dependencies and PHP extensions
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    docker-php-ext-install pdo pdo_mysql

# Enable Apache rewrite module
RUN a2enmod rewrite

# Configure Apache virtual host
RUN printf '<VirtualHost *:80>\n\
    DocumentRoot /var/www/html\n\
    <Directory /var/www/html>\n\
        AllowOverride All\n\
        Require all granted\n\
    </Directory>\n\
    ErrorLog /dev/stderr\n\
    CustomLog /dev/null combined\n\
    ServerSignature Off\n\
    ServerTokens Prod\n\
</VirtualHost>\n' > /etc/apache2/sites-available/000-default.conf

# Disable server signature, version headers, and PHP exposure
RUN printf 'ServerTokens Prod\nServerSignature Off\n' >> /etc/apache2/apache2.conf && \
    echo 'expose_php = Off' > /usr/local/etc/php/conf.d/security.ini

# Copy application files
COPY config.php /var/www/html/config.php
COPY index.php /var/www/html/index.php
COPY core/ /var/www/html/core/
COPY admin/ /var/www/html/admin/
COPY employee/ /var/www/html/employee/
COPY pages/ /var/www/html/pages/
COPY public/ /var/www/html/public/

# Create .htaccess for URL routing
RUN printf 'RewriteEngine On\nRewriteCond %%{REQUEST_FILENAME} !-f\nRewriteCond %%{REQUEST_FILENAME} !-d\nRewriteRule ^(.*)$ /index.php [QSA,L]\n' > /var/www/html/.htaccess

# Plant the flag at build time only - NOT available as runtime env var
ARG FLAG
RUN mkdir -p /opt/data && \
    echo -n "${FLAG}" > /opt/data/credentials && \
    chmod 444 /opt/data/credentials && \
    chown www-data:www-data /opt/data/credentials

# Copy startup script
COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh

# Set proper ownership
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80

CMD ["/usr/local/bin/startup.sh"]
