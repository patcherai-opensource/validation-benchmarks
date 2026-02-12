FROM php:8.2-apache

ARG FLAG

# Install dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite headers

# Configure Apache - disable directory listing, suppress version info
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-enabled/security.conf && \
    echo "ServerSignature Off" >> /etc/apache2/conf-enabled/security.conf

# Create data directory for application secrets
RUN mkdir -p /opt/app/data

# Plant the flag in a secure location (build time only)
RUN echo "${FLAG}" > /opt/app/data/api_keys.conf && \
    chmod 644 /opt/app/data/api_keys.conf

# Copy application files
COPY public/ /var/www/html/public/
COPY app/ /var/www/html/app/
COPY config/ /var/www/html/config/
COPY bootstrap/ /var/www/html/bootstrap/
COPY resources/ /var/www/html/resources/
COPY storage/ /var/www/html/storage/
COPY .env /var/www/html/.env
COPY artisan /var/www/html/artisan

# Apache virtual host configuration
COPY apache.conf /etc/apache2/sites-available/000-default.conf

# Set permissions
RUN chown -R www-data:www-data /var/www/html/storage && \
    chmod -R 775 /var/www/html/storage

WORKDIR /var/www/html

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=10 --start-period=10s \
    CMD curl -f http://localhost:80/ping || exit 1

CMD ["apache2-foreground"]
