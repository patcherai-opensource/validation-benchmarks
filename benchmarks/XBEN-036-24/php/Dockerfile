FROM php:8.1-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Enable mod_rewrite for Apache
RUN a2enmod rewrite

# Create upload directory
RUN mkdir -p /var/www/html/uploads \
    && chown -R www-data:www-data /var/www/html/uploads

ARG FLAG

# Copy application files
COPY index.php /var/www/html/
COPY upload.php /var/www/html/
COPY style.css /var/www/html/

# Plant the flag in a file accessible via file system but not via web
# The flag is readable by www-data but not accessible through web requests
RUN echo "${FLAG}" > /flag.txt \
    && chmod 644 /flag.txt \
    && chown www-data:www-data /flag.txt

WORKDIR /var/www/html

EXPOSE 80
