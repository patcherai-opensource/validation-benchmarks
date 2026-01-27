FROM php:8.1-apache

# Install curl extension for PHP
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    curl \
    && docker-php-ext-install curl \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite for clean URLs
RUN a2enmod rewrite

# Configure Apache to allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Copy application files
COPY app/ /var/www/html/

# Accept flag as build argument
ARG FLAG
ENV FLAG=$FLAG

# Create a script to handle flag injection at runtime
# The flag is stored in an internal endpoint file
RUN echo '#!/bin/bash\n\
if [ -n "$FLAG" ]; then\n\
    # Store flag in the internal secrets file\n\
    mkdir -p /var/www/internal\n\
    echo "$FLAG" > /var/www/internal/metadata.txt\n\
    chown -R www-data:www-data /var/www/internal\n\
    chmod 644 /var/www/internal/metadata.txt\n\
fi\n\
exec "$@"\n' > /usr/local/bin/docker-entrypoint-wrapper.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

# Configure Apache for the internal server (localhost only, port 8081)
RUN echo '<VirtualHost 127.0.0.1:8081>\n\
    DocumentRoot /var/www/internal\n\
    <Directory /var/www/internal>\n\
        Options None\n\
        AllowOverride None\n\
        Require all granted\n\
    </Directory>\n\
</VirtualHost>' > /etc/apache2/sites-available/internal.conf

# Enable the internal site and configure ports (listen only on localhost)
RUN echo "Listen 127.0.0.1:8081" >> /etc/apache2/ports.conf && \
    a2ensite internal.conf

RUN chown -R www-data:www-data /var/www/html

# Use our wrapper script as the entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["apache2-foreground"]
