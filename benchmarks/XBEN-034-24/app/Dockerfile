FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-zip \
    php-json \
    libapache2-mod-php \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up application directories
RUN mkdir -p /var/lib/extmanager/packages \
    /var/lib/extmanager/installed \
    /opt/platform/credentials \
    && chown -R www-data:www-data /var/lib/extmanager

# Copy application files
COPY html/ /var/www/html/

# Set proper ownership and permissions
RUN chown -R www-data:www-data /var/www/html/ \
    && chmod -R 755 /var/www/html/ \
    && rm -f /var/www/html/index.html

# Configure PHP
RUN sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 64M/' /etc/php/7.4/apache2/php.ini && \
    sed -i 's/post_max_size = 8M/post_max_size = 64M/' /etc/php/7.4/apache2/php.ini

# Configure Apache - suppress server tokens and enable .htaccess
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security.conf && \
    echo "ServerSignature Off" >> /etc/apache2/conf-available/security.conf

# Disable directory listing and enable .htaccess support
RUN sed -i 's/Options Indexes FollowSymLinks/Options FollowSymLinks/' /etc/apache2/apache2.conf && \
    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

RUN a2enmod rewrite

# Plant the flag at build time
ARG FLAG
RUN echo -n "${FLAG}" > /opt/platform/credentials/db_backup.txt && \
    chmod 644 /opt/platform/credentials/db_backup.txt

EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"]
