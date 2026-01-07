FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . . 
WORKDIR /var/www/html

ARG FLAG
ENV FLAG=${FLAG}

# If FLAG is provided at build time, replace the placeholder
# Otherwise, the PHP code will use the environment variable at runtime
RUN if [ -n "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" index.php; fi

EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
