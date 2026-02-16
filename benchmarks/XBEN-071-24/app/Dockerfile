FROM php:8.3.6-apache

RUN apt-get update && apt-get install -y netcat-traditional curl && \
    rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install mysqli

COPY . /var/www/html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Remove development artifacts
RUN rm -f /var/www/html/entrypoint.sh /var/www/html/Dockerfile

RUN chown -R www-data:www-data /var/www/html

# Disable directory listing and server signature
RUN a2dismod autoindex 2>/dev/null || true
RUN echo "ServerSignature Off" >> /etc/apache2/apache2.conf && \
    echo "ServerTokens Prod" >> /etc/apache2/apache2.conf

ENTRYPOINT ["/entrypoint.sh"]
