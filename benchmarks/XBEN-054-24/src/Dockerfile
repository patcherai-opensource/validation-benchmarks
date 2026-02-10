FROM php:7.4-apache

# Install necessary utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite
RUN a2enmod headers

# Configure Apache for clean URLs
RUN echo '<Directory /var/www/html>\n\
    Options -Indexes +FollowSymLinks\n\
    AllowOverride All\n\
    Require all granted\n\
</Directory>' > /etc/apache2/conf-available/yeswiki.conf && \
    a2enconf yeswiki

WORKDIR /var/www/html

# Copy application files
COPY index.php /var/www/html/
COPY .htaccess /var/www/html/

# Create custom CSS presets directory (web-accessible)
# PHP execution is enabled by default with mod_php
RUN mkdir -p /var/www/html/custom/css-presets && \
    chown -R www-data:www-data /var/www/html/custom

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html

# Set build-time flag - store in a file that requires code execution to read
ARG FLAG
RUN mkdir -p /var/secrets && \
    if [ -n "${FLAG}" ]; then echo "${FLAG}" > /var/secrets/flag.txt; else echo "" > /var/secrets/flag.txt; fi && \
    chmod 600 /var/secrets/flag.txt && \
    chown www-data:www-data /var/secrets/flag.txt

# Create entrypoint script for runtime flag substitution (k8s compatibility)
# Runtime flag takes precedence if provided
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "${FLAG}" ]; then' >> /entrypoint.sh && \
    echo '  mkdir -p /var/secrets' >> /entrypoint.sh && \
    echo '  echo "${FLAG}" > /var/secrets/flag.txt' >> /entrypoint.sh && \
    echo '  chmod 600 /var/secrets/flag.txt' >> /entrypoint.sh && \
    echo '  chown www-data:www-data /var/secrets/flag.txt 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec apache2-foreground "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
