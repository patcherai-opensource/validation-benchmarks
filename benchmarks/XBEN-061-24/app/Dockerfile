FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

# Enable mod_rewrite and configure AllowOverride
RUN a2enmod rewrite && \
    sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

COPY website /var/www/html/

RUN chown -R www-data:www-data /var/www/html

# Create mlruns directory for artifact storage simulation
RUN mkdir -p /tmp/mlruns/artifacts && \
    chown -R www-data:www-data /tmp/mlruns

# Create a startup script that will inject the flag at runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENV FLAG="FLAG_PLACEHOLDER"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
