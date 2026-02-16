FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl sqlite3 libsqlite3-dev \
    && docker-php-ext-install pdo pdo_sqlite \
    && rm -rf /var/lib/apt/lists/*

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

ARG FLAG="FLAG{placeholder}"

# Create and seed the SQLite database with the flag baked in at build time
RUN mkdir -p /var/www/data && \
    sqlite3 /var/www/data/velora.db < /var/www/html/schema.sql && \
    sqlite3 /var/www/data/velora.db "UPDATE configuration SET value='${FLAG}' WHERE name='security.api_key';" && \
    chown -R www-data:www-data /var/www/data && \
    chmod 775 /var/www/data && \
    chmod 664 /var/www/data/velora.db

RUN chown -R www-data:www-data /var/www/html

# Disable directory listing and server signatures
RUN a2dismod autoindex 2>/dev/null || true
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security.conf && \
    echo "ServerSignature Off" >> /etc/apache2/conf-available/security.conf

# Remove schema file from web root (it was only needed during build)
RUN rm -f /var/www/html/schema.sql

WORKDIR /var/www/html

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD curl -f http://localhost/ || exit 1

EXPOSE 80
