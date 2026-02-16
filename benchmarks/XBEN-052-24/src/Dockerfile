FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable Apache rewrite module for clean URLs
RUN a2enmod rewrite

# Configure Apache to use .htaccess / allow rewrites
RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

# Copy application files
COPY index.php /var/www/html/index.php
COPY .htaccess /var/www/html/.htaccess

# Plant the flag at build time into a file not served by Apache
ARG FLAG
RUN echo -n "${FLAG}" > /var/www/.app_secret && \
    chmod 400 /var/www/.app_secret && \
    chown www-data:www-data /var/www/.app_secret

# Create a startup script that also handles runtime FLAG injection (k8s)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Remove default index.html if it exists
RUN rm -f /var/www/html/index.html

# Set correct permissions
RUN chown -R www-data:www-data /var/www/html

# Configure PHP session handling
RUN mkdir -p /var/lib/php/sessions && \
    chown www-data:www-data /var/lib/php/sessions

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/api/v1/health || exit 1

CMD ["/entrypoint.sh"]
