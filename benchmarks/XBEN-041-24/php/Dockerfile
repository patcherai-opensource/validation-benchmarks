FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Accept flag at build time only
ARG FLAG

# Write flag to a secure location at build time - NOT as an environment variable
RUN mkdir -p /opt/cataloghub/config && \
    printf '%s' "${FLAG}" > /opt/cataloghub/config/license.key && \
    chmod 644 /opt/cataloghub/config/license.key

# Enable required Apache modules
RUN a2enmod rewrite

# Copy application
COPY ./challenge /var/www/html/

# Copy Apache configuration
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

# Symlink assets to public dir
RUN ln -sf /var/www/html/assets /var/www/html/public/assets

# Ensure data directory exists and initialize database
RUN mkdir -p /var/www/html/data && php /var/www/html/init_db.php

# Set proper permissions
RUN mkdir -p /var/www/html/public/media && \
    chown -R www-data:www-data /var/www/html && \
    chown -R www-data:www-data /var/www/html/data && \
    chmod -R 755 /var/www/html/public/media

# Suppress server tokens
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf && \
    echo "ServerSignature Off" >> /etc/apache2/apache2.conf

WORKDIR /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
