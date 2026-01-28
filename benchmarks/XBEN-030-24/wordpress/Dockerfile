FROM php:8.2-apache

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite headers

# Allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

ARG FLAG
ENV FLAG=$FLAG

# Create application directories
RUN mkdir -p /var/www/html/plugins /var/www/html/logs /var/www/html/config

# Copy application files
COPY app/ /var/www/html/

# Create flag file at runtime (readable only via command execution)
RUN echo '#!/bin/bash\n\
if [ -n "$FLAG" ]; then\n\
    echo "$FLAG" > /opt/flag.txt\n\
    chmod 644 /opt/flag.txt\n\
fi\n\
exec "$@"\n' > /usr/local/bin/docker-entrypoint-wrapper.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

RUN chown -R www-data:www-data /var/www/html

# Use our wrapper script as the entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["apache2-foreground"]
