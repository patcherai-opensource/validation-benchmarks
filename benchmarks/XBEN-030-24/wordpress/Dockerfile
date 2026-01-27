FROM php:8.1-apache

# Install git for the plugin installation feature
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite for clean URLs
RUN a2enmod rewrite

# Configure Apache for routing
RUN printf '<Directory /var/www/html>\n    Options Indexes FollowSymLinks\n    AllowOverride All\n    Require all granted\n</Directory>\n' > /etc/apache2/conf-available/app.conf && a2enconf app

# Copy application files
COPY index.php admin.php /var/www/html/

# Create .htaccess for URL routing
RUN printf 'RewriteEngine On\nRewriteCond %%{REQUEST_FILENAME} !-f\nRewriteCond %%{REQUEST_FILENAME} !-d\nRewriteRule ^(.*)$ /index.php [L,QSA]\n' > /var/www/html/.htaccess

# Accept FLAG as build argument and create wrapper to write it at runtime
ARG FLAG
ENV FLAG=$FLAG

# Create entrypoint wrapper to handle flag injection
RUN printf '#!/bin/bash\nif [ -n "$FLAG" ]; then\n    echo "$FLAG" > /opt/flag.txt\n    chmod 644 /opt/flag.txt\nfi\nexec "$@"\n' > /usr/local/bin/docker-entrypoint-wrapper.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

# Set proper ownership
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["apache2-foreground"]
