FROM php:8.2-apache

ARG FLAG

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite headers

# Copy Apache virtual host configuration
COPY apache-vhost.conf /etc/apache2/sites-available/000-default.conf

# Suppress server signature
RUN echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/apache2.conf

# Copy application files
COPY . /var/www/html/

# Plant the flag in a secure location at build time
RUN mkdir -p /var/secrets && \
    echo "${FLAG}" > /var/secrets/app_flag.txt && \
    chmod 444 /var/secrets/app_flag.txt

# Set permissions
RUN chown -R www-data:www-data /var/www/html/storage && \
    chmod -R 775 /var/www/html/storage

WORKDIR /var/www/html

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=10 --start-period=10s \
    CMD curl -f http://localhost:80/health || exit 1

CMD ["apache2-foreground"]
