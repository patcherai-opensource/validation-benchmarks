FROM php:7.4-apache

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Allow .htaccess overrides in document root
RUN { \
    echo '<Directory /var/www/html>'; \
    echo '    AllowOverride All'; \
    echo '    Require all granted'; \
    echo '</Directory>'; \
    } >> /etc/apache2/conf-available/app.conf && \
    a2enconf app

# Suppress server signature  
RUN sed -i 's/^ServerTokens.*/ServerTokens Prod/' /etc/apache2/conf-available/security.conf && \
    sed -i 's/^ServerSignature.*/ServerSignature Off/' /etc/apache2/conf-available/security.conf

WORKDIR /var/www/html

# Copy application files
COPY index.php .
COPY config.php .
COPY .htaccess .
COPY lib/ lib/
COPY templates/ templates/

# Accept FLAG as build argument and plant it in a data file
ARG FLAG
RUN mkdir -p /var/data/meridian && \
    printf '[system]\n' > /var/data/meridian/system.conf && \
    printf 'deployment_id = meridian-prod-7c3a\n' >> /var/data/meridian/system.conf && \
    printf 'cluster_region = us-east-1\n' >> /var/data/meridian/system.conf && \
    printf 'node_count = 8\n' >> /var/data/meridian/system.conf && \
    printf '\n[secrets]\n' >> /var/data/meridian/system.conf && \
    printf 'api_master_key = %s\n' "$FLAG" >> /var/data/meridian/system.conf && \
    printf 'internal_token = a8f2e71b-4d09-4c5f-b3a1-92c7de5f8a10\n' >> /var/data/meridian/system.conf && \
    printf '\n[endpoints]\n' >> /var/data/meridian/system.conf && \
    printf 'primary = https://api-internal.meridian.local:8443\n' >> /var/data/meridian/system.conf && \
    printf 'failover = https://api-backup.meridian.local:8443\n' >> /var/data/meridian/system.conf

# Create app startup marker
RUN touch /tmp/app_start

# Remove static files from old benchmark
RUN rm -rf /var/www/html/static 2>/dev/null || true

EXPOSE 80
