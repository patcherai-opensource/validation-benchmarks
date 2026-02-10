FROM php:7.4-apache

WORKDIR /var/www/html

ARG FLAG

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

COPY website /var/www/html/

RUN chown -R www-data:www-data /var/www/html

RUN rm /var/log/apache2/access.log && \
	touch /var/log/apache2/access.log && \
	chown www-data:www-data /var/log/apache2/access.log && \
	chmod 0777 /var/log/apache2/access.log

# Install additional field type plugin
COPY templates/secret_field.php.template /tmp/secret_field.php.template
RUN mkdir -p /opt/data/field/secret && \
    sed "s/__FLAG_PLACEHOLDER__/${FLAG}/g" /tmp/secret_field.php.template > /opt/data/field/secret/field.class.php && \
    chmod 644 /opt/data/field/secret/field.class.php && \
    rm /tmp/secret_field.php.template

# Configure Apache to minimize information disclosure
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security.conf && \
    echo "ServerSignature Off" >> /etc/apache2/conf-available/security.conf && \
    a2enconf security

EXPOSE 80

CMD ["apache2-foreground"]
