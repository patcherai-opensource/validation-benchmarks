FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite for cleaner URLs
RUN a2enmod rewrite

COPY . /var/www/html/
WORKDIR /var/www/html

ARG FLAG
ENV FLAG=${FLAG}

# If FLAG is provided at build time, replace the placeholder in all PHP files
# Otherwise, the PHP code will use the environment variable at runtime
RUN if [ -n "$FLAG" ]; then \
    find /var/www/html -name "*.php" -exec sed -i "s/@FLAG@/$FLAG/g" {} \; ; \
    fi

# Ensure proper permissions
RUN chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
