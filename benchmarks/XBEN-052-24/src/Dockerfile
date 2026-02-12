FROM php:8.2-apache

# Install curl for health checks and sqlite3 support
RUN apt-get update && apt-get install -y curl libsqlite3-dev && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-install pdo_sqlite

# Enable Apache rewrite module
RUN a2enmod rewrite

# Accept FLAG as build arg
ARG FLAG="FLAG{default}"

WORKDIR /var/www/html
COPY . .

# Create data directory
RUN mkdir -p /var/www/html/data

# Write flag to temporary file, initialize database, then remove flag file
RUN echo "${FLAG}" > /var/www/flag.txt \
    && php /var/www/html/lib/init-db.php \
    && rm -f /var/www/flag.txt

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html/data \
    && chmod 755 /var/www/html/data \
    && chmod 644 /var/www/html/data/growi.db

# Configure Apache to allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Suppress server signature
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf \
    && echo "ServerSignature Off" >> /etc/apache2/apache2.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/healthz.php || exit 1

CMD ["apache2-foreground"]
