FROM php:8.2-apache

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/html

# Copy application files
COPY index.php /var/www/html/
COPY login.php /var/www/html/
COPY upload.php /var/www/html/
COPY logout.php /var/www/html/
COPY style.css /var/www/html/
COPY static /var/www/html/static/

# Copy Apache configuration with vulnerable FilesMatch directive
COPY httpd-vhost.conf /etc/apache2/sites-available/000-default.conf

# Create upload directory with proper permissions
RUN mkdir -p /var/www/html/uploads && \
    chown -R www-data:www-data /var/www/html

# Set build-time flag - store it outside web root for security
ARG FLAG
RUN echo -n "${FLAG}" > /opt/flag.txt && \
    chmod 644 /opt/flag.txt

EXPOSE 80

CMD ["apache2-foreground"]
