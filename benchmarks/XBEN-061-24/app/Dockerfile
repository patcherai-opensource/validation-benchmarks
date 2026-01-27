FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

# Enable short_open_tag for PHP
RUN echo "short_open_tag = On" >> /usr/local/etc/php/conf.d/short-tags.ini

COPY website /var/www/html/

RUN chown -R www-data:www-data /var/www/html

# Create directories for artifacts and secrets
RUN mkdir -p /data/artifacts /data/secrets && \
    chown -R www-data:www-data /data

# Create a startup script that will inject the flag at runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENV FLAG="FLAG_PLACEHOLDER"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
