FROM php:8.1-apache

ARG FLAG

# Install required packages
RUN apt-get update && apt-get install -y \
    sudo \
    wireguard-tools \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /var/www/html

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html

# Suppress PHP information leakage
RUN cp /var/www/html/php-config.ini /usr/local/etc/php/conf.d/security.ini && \
    rm -f /var/www/html/php-config.ini /var/www/html/Dockerfile

# Configure Apache - suppress server tokens
RUN a2enmod rewrite && \
    echo 'ServerName localhost' >> /etc/apache2/apache2.conf && \
    echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/apache2.conf

# Create wireguard directory structure
RUN mkdir -p /etc/wireguard && \
    chown www-data:www-data /etc/wireguard

# Allow www-data to run commands via sudo without password (network management)
RUN echo 'www-data ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Plant flag at build time if provided as build arg
RUN if [ -n "$FLAG" ]; then \
        echo "$FLAG" > /opt/flag.txt; \
        chmod 644 /opt/flag.txt; \
    fi

# Create entrypoint wrapper that plants the flag at runtime (for K8s env var injection)
RUN printf '#!/bin/bash\nif [ -n "$FLAG" ] && [ ! -s /opt/flag.txt ]; then\n    echo "$FLAG" > /opt/flag.txt\n    chmod 644 /opt/flag.txt\nfi\nunset FLAG\nexec "$@"\n' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["apache2-foreground"]
