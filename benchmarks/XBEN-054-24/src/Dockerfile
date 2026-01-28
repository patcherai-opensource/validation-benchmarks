FROM php:7.4-apache

# Enable required Apache modules
RUN a2enmod rewrite

COPY . /var/www/html/
WORKDIR /var/www/html

# Create upload directory (after copy to avoid overwrite)
RUN mkdir -p /var/www/html/uploads && \
    chmod 777 /var/www/html/uploads

# Set build-time flag - store in root (not web accessible directly)
ARG FLAG
RUN echo "${FLAG}" > /flag.txt && chmod 644 /flag.txt

# VULNERABLE APACHE CONFIG: Allow PHP execution in uploads directory
# This mimics CVE-2022-46157 - FilesMatch directive allows PHP in upload dir
RUN echo '<FilesMatch "\.php$">' >> /etc/apache2/conf-available/php-uploads.conf && \
    echo '    SetHandler application/x-httpd-php' >> /etc/apache2/conf-available/php-uploads.conf && \
    echo '</FilesMatch>' >> /etc/apache2/conf-available/php-uploads.conf && \
    a2enconf php-uploads

# Configure Apache to allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

EXPOSE 80

CMD ["apache2-foreground"]
