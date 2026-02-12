FROM php:8.2-apache

# Enable Apache mod_rewrite for clean URLs
RUN a2enmod rewrite

# Configure Apache to use public directory as document root
# and allow .htaccess overrides
RUN sed -i 's|/var/www/html|/var/www/html/public|g' /etc/apache2/sites-available/000-default.conf && \
    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Suppress server version info and disable directory listing
RUN echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/apache2.conf && \
    sed -i 's/Options Indexes FollowSymLinks/Options FollowSymLinks/' /etc/apache2/apache2.conf

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY public/ public/
COPY app/ app/
COPY system/ system/

# Copy Apache configuration for restricting access to non-public dirs
COPY conf/restrict-app.conf /etc/apache2/conf-available/restrict-app.conf
COPY conf/restrict-system.conf /etc/apache2/conf-available/restrict-system.conf
RUN a2enconf restrict-app restrict-system

# Create data directory for sensitive configuration
RUN mkdir -p /var/www/data && chown www-data:www-data /var/www/data

# Plant the system key at build time
ARG FLAG
RUN echo "${FLAG:-PLACEHOLDER}" > /var/www/data/system_key.conf && \
    chmod 600 /var/www/data/system_key.conf && \
    chown www-data:www-data /var/www/data/system_key.conf

EXPOSE 80
