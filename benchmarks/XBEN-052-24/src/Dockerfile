FROM php:8.2-apache

# Install curl for health checks and sqlite3
RUN apt-get update && apt-get install -y curl sqlite3 && rm -rf /var/lib/apt/lists/*

# Enable SQLite3 for PHP (already included in php:8.2-apache)

WORKDIR /var/www/html

COPY . .

# Build argument for flag injection at build time
ARG FLAG="FLAG{placeholder}"

# Substitute the flag at build time (not runtime)
RUN sed -i "s/@FLAG@/${FLAG}/g" /var/www/html/index.php

# Ensure proper permissions
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    mkdir -p /tmp && chmod 1777 /tmp

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

CMD ["apache2-foreground"]
