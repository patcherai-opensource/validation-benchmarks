FROM php:7.4-apache

RUN apt-get update -y && \
    apt-get install -y curl libcurl4-openssl-dev pkg-config && \
    docker-php-ext-install curl && \
    a2enmod rewrite && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /var/www/html/

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html

# Apache config
RUN printf '<Directory /var/www/html>\n    AllowOverride All\n    Require all granted\n</Directory>\nServerTokens Prod\nServerSignature Off\n' > /etc/apache2/conf-available/axis.conf && \
    a2enconf axis

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/ || exit 1
