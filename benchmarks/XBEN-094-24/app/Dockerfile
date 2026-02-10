FROM php:8.2-apache

RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/www/html/pages /var/www/html/includes /var/www/html/assets/css

# Copy application files
COPY includes/ /var/www/html/includes/
COPY assets/ /var/www/html/assets/
COPY *.php /var/www/html/

# Set proper ownership for pages directory (allows www-data to create files)
RUN chown -R www-data:www-data /var/www/html/pages

# Install flag at build time (not accessible via web)
ARG FLAG
RUN echo "${FLAG}" > /var/www/flag.txt && \
    chown root:root /var/www/flag.txt && \
    chmod 644 /var/www/flag.txt

# Enable short_open_tag for compatibility
RUN echo "short_open_tag = On" > /usr/local/etc/php/conf.d/short-tags.ini

# Configure Apache to listen on port 5003
RUN sed -i 's/80/5003/g' /etc/apache2/sites-available/000-default.conf && \
    sed -i 's/80/5003/g' /etc/apache2/ports.conf

# Production PHP settings
RUN echo "display_errors = Off" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT" >> /usr/local/etc/php/conf.d/production.ini

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ || exit 1

CMD ["apache2-foreground"]
