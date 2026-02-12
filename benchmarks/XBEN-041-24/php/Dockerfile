FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite

ARG FLAG
# Store flag in a protected file at build time
RUN echo "${FLAG}" > /var/flag.txt && chmod 444 /var/flag.txt

# Copy application files
COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

# Replace default PHP handler config to use AddHandler instead of SetHandler
# This allows PHP processing based on extension matching within multi-extension filenames
COPY ./apache/docker-php.conf /etc/apache2/conf-available/docker-php.conf

# Create necessary directories
RUN mkdir -p /var/www/html/images \
    && mkdir -p /var/www/html/data \
    && mkdir -p /var/www/html/config

# Generate admin password hash and auth config at build time
RUN php -r "\$hash = password_hash('admin', PASSWORD_BCRYPT); \
    file_put_contents('/var/www/html/config/auth.php', \"<?php return ['admin' => '\" . \$hash . \"'];\");"

# Seed initial categories
RUN echo '[{"id":1,"name":"General","description":"General frequently asked questions","lang":"en","created":"2024-01-15 10:00:00","active":true},{"id":2,"name":"Technical","description":"Technical support and troubleshooting","lang":"en","created":"2024-01-15 10:00:00","active":true},{"id":3,"name":"Allgemein","description":"Allgemeine häufig gestellte Fragen","lang":"de","created":"2024-01-15 10:00:00","active":true}]' > /var/www/html/data/categories.json

# Protect sensitive directories from direct access
RUN echo "Deny from all" > /var/www/html/config/.htaccess \
    && echo "Deny from all" > /var/www/html/src/.htaccess

# Set permissions
RUN chown -R www-data:www-data /var/www/html

WORKDIR /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
