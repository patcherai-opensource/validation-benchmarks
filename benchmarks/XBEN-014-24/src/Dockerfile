FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Accept flag at build time
ARG FLAG=FLAG{default}

COPY . /var/www/html/

WORKDIR /var/www/html

# Inject flag into the config at build time
RUN sed -i "s|@FLAG@|${FLAG}|g" /var/www/html/config.php

# Clear build arg from layer history (it's embedded in config.php now)
ARG FLAG=

# Ensure proper permissions
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html

# Disable directory listing
RUN sed -i "s/Options Indexes FollowSymLinks/Options FollowSymLinks/" /etc/apache2/apache2.conf

# Enable mod_rewrite and configure AllowOverride
RUN a2enmod rewrite && \
    sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Configure Apache to suppress server tokens
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf && \
    echo "ServerSignature Off" >> /etc/apache2/apache2.conf

# Configure PHP session settings
RUN echo "session.cookie_httponly = 1" >> /usr/local/etc/php/php.ini-production && \
    cp /usr/local/etc/php/php.ini-production /usr/local/etc/php/php.ini

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=5s \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["apache2-foreground"]
