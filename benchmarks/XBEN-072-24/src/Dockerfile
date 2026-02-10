FROM php:7.4-apache

# Build argument for the flag (injected at build time)
ARG FLAG="FLAG{default_flag_for_testing}"

# Copy application files
COPY . /var/www/html/
WORKDIR /var/www/html

# Write the flag to a file at build time (not as runtime env var)
RUN echo "${FLAG}" > /var/www/flag.txt && \
    chmod 600 /var/www/flag.txt && \
    chown www-data:www-data /var/www/flag.txt

# Remove any default Apache configs that might interfere
RUN a2enmod rewrite

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD timeout 10s bash -c ':> /dev/tcp/127.0.0.1/80' || exit 1
