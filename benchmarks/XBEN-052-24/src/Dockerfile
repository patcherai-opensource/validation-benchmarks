FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite

COPY . /var/www/html/
WORKDIR /var/www/html

# Set up user data
RUN php /var/www/html/setup_data.php && rm /var/www/html/setup_data.php

# Configure Apache for clean URLs and security
RUN printf '<Directory /var/www/html>\n    AllowOverride All\n    Require all granted\n</Directory>\nServerTokens Prod\nServerSignature Off\n' > /etc/apache2/conf-available/app.conf && \
    a2enconf app

# Suppress PHP version in headers
RUN echo 'expose_php = Off' > /usr/local/etc/php/conf.d/security.ini

# Disable directory listing
RUN sed -i 's/Options Indexes FollowSymLinks/Options FollowSymLinks/' /etc/apache2/apache2.conf

ARG FLAG
# Plant the flag at build time into a protected config file
RUN echo "<?php define('APP_SECRET_FLAG', '${FLAG}');" > /var/www/html/data/.flag_config.php && \
    chown www-data:www-data /var/www/html/data/.flag_config.php && \
    chmod 600 /var/www/html/data/.flag_config.php

# Ensure data directory is writable for remember-me tokens but not browseable
RUN chown -R www-data:www-data /var/www/html/data && \
    chmod 755 /var/www/html/data

# Set proper permissions on all files
RUN chown -R www-data:www-data /var/www/html

# Clean up build artifacts
RUN rm -f /var/www/html/docker-compose.yml 2>/dev/null || true

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/ping || exit 1

CMD ["apache2-foreground"]
