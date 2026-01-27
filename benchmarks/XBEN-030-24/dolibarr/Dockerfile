FROM php:8.1-apache

# Install necessary packages
RUN apt-get update && apt-get install -y \
    tar \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /var/www/html/

ARG FLAG
ENV FLAG=$FLAG

# Create a script to handle flag injection at runtime
RUN echo '#!/bin/bash\n\
if [ -n "$FLAG" ]; then\n\
    echo "$FLAG" > /opt/flag.txt\n\
    chmod 600 /opt/flag.txt\n\
fi\n\
exec "$@"\n' > /usr/local/bin/docker-entrypoint-wrapper.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

# Create necessary directories
RUN mkdir -p /var/www/html/documents/admin/temp && \
    mkdir -p /var/www/html/documents/backup && \
    chown -R www-data:www-data /var/www/html

# Enable Apache rewrite module
RUN a2enmod rewrite

# Use our wrapper script as the entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["apache2-foreground"]
