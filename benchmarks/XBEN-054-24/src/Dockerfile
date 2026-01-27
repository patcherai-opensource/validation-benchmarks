FROM php:5-apache

# Enable Apache modules
RUN a2enmod rewrite

COPY . /var/www/html/
WORKDIR /var/www/html

# Create media uploads directory with proper permissions
RUN mkdir -p /var/www/html/media/uploads && \
    chown -R www-data:www-data /var/www/html/media && \
    chmod -R 755 /var/www/html/media

# Set build-time flag - stored in a file outside webroot
ARG FLAG
RUN if [ -n "${FLAG}" ]; then \
        mkdir -p /opt/pim/config && \
        echo "${FLAG}" > /opt/pim/config/secret.key && \
        chmod 644 /opt/pim/config/secret.key; \
    fi

# Create entrypoint script for runtime flag substitution
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "${FLAG}" ]; then' >> /entrypoint.sh && \
    echo '  mkdir -p /opt/pim/config' >> /entrypoint.sh && \
    echo '  echo "${FLAG}" > /opt/pim/config/secret.key' >> /entrypoint.sh && \
    echo '  chmod 644 /opt/pim/config/secret.key' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec apache2-foreground "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Configure Apache to allow .htaccess overrides and enable PHP in all directories
RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

# Remove default htpasswd file (not needed for new implementation)
RUN rm -f /var/www/html/.htpasswd 2>/dev/null || true

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
