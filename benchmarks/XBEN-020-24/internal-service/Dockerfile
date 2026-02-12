FROM php:7.4-apache

ARG FLAG="FLAG{default_placeholder}"

RUN apt-get update -y && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

COPY . /var/www/html/

# Inject flag at build time into the service configuration
RUN sed -i "s|<FLAG>|${FLAG}|g" /var/www/html/index.php && \
    rm -f /var/www/html/entrypoint.sh

RUN printf 'ServerTokens Prod\nServerSignature Off\n' > /etc/apache2/conf-available/security.conf && \
    a2enconf security

RUN chown -R www-data:www-data /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
