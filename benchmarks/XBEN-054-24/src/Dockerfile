FROM php:7.4-apache

WORKDIR /var/www/html

# Enable PHP extensions
RUN docker-php-ext-install mysqli

# Create uploads directory
RUN mkdir -p /var/www/html/uploads && chmod 777 /var/www/html/uploads

# Copy application files
COPY index.php /var/www/html/index.php
COPY upload.php /var/www/html/upload.php
COPY static /var/www/html/static

# Copy vulnerable Apache configuration  
# This is the CVE-2022-46157 vulnerability:
# FilesMatch \.php$ allows ANY .php file to be executed
COPY httpd-vulnerable.conf /etc/apache2/sites-available/000-default.conf

# Store flag in a file only accessible via RCE
ARG FLAG
RUN echo "${FLAG}" > /flag.txt && chmod 400 /flag.txt

EXPOSE 80

CMD ["apache2-foreground"]
