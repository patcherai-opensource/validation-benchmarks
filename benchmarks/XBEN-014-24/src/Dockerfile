FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy start script
COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

WORKDIR /var/www/html

# Copy only the web files (not Dockerfile or start.sh)
COPY index.php /var/www/html/
COPY static/ /var/www/html/static/

# Remove default Apache files and ensure proper permissions
RUN rm -rf /var/www/html/index.html && \
    chown -R www-data:www-data /var/www/html

EXPOSE 80

# Health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=5s \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/usr/local/bin/start.sh"]
