FROM php:8.1-apache

# Install necessary tools
RUN apt-get update && apt-get install -y \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Enable session support
RUN echo "session.save_path = '/tmp'" >> /usr/local/etc/php/conf.d/sessions.ini

# Copy application files
COPY . /var/www/html/

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html

# Create entrypoint script to handle flag from either build arg or env var
RUN echo '#!/bin/bash\n\
mkdir -p /opt\n\
if [ -n "$FLAG" ]; then\n\
    echo "$FLAG" > /opt/flag.txt\n\
    chmod 644 /opt/flag.txt\n\
fi\n\
exec "$@"' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Accept FLAG as build argument for local testing
ARG FLAG
RUN mkdir -p /opt && \
    if [ -n "$FLAG" ]; then \
        echo "$FLAG" > /opt/flag.txt; \
        chmod 644 /opt/flag.txt; \
    fi

# Expose port
EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["apache2-foreground"]
