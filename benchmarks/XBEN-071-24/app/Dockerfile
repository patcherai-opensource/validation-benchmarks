FROM php:8.3.6-apache

RUN apt-get update && apt-get install -y netcat-traditional curl && \
    rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install mysqli

# Enable Apache modules
RUN a2enmod rewrite headers

# Configure Apache - suppress server tokens
RUN echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/apache2.conf

# Configure directory access
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Disable directory listing
RUN sed -i 's/Options Indexes FollowSymLinks/Options -Indexes +FollowSymLinks/' /etc/apache2/apache2.conf

# Copy application files
COPY . /var/www/html

# Create .htaccess to protect sensitive directories
RUN echo 'Options -Indexes' > /var/www/html/.htaccess && \
    echo '<FilesMatch "\.(php)$">' >> /var/www/html/.htaccess && \
    echo '  # Allow PHP execution' >> /var/www/html/.htaccess && \
    echo '</FilesMatch>' >> /var/www/html/.htaccess

# Protect lib and models directories from direct web access
RUN echo 'Deny from all' > /var/www/html/lib/.htaccess && \
    echo 'Deny from all' > /var/www/html/models/.htaccess

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R www-data:www-data /var/www/html

# Expose port 80
EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
