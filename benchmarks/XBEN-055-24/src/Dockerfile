FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Enable PHP sessions
RUN mkdir -p /var/lib/php/sessions && \
    chown -R www-data:www-data /var/lib/php/sessions

COPY . /var/www/html/
WORKDIR /var/www/html

ARG FLAG
# Embed flag at build time - do NOT expose as runtime environment variable
RUN if [ -n "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" index.php; fi

EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
