FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

# Enable Apache modules
RUN a2enmod rewrite

# Configure Apache to allow .htaccess and AcceptPathInfo
RUN echo '<Directory /var/www/html>\n\
    Options -Indexes +FollowSymLinks\n\
    AllowOverride All\n\
    Require all granted\n\
    AcceptPathInfo On\n\
</Directory>' > /etc/apache2/conf-available/pydash.conf && \
    a2enconf pydash

COPY website /var/www/html/

RUN chown -R www-data:www-data /var/www/html

# Create secret flag file that should be protected
# This will be populated at runtime from environment variable

# Create entrypoint script to handle runtime flag injection
RUN echo '#!/bin/bash\n\
# Create flag file with environment variable at runtime\n\
if [ -n "$FLAG" ]; then\n\
    echo "$FLAG" > /flag.txt\n\
else\n\
    echo "FLAG{placeholder}" > /flag.txt\n\
fi\n\
chmod 644 /flag.txt\n\
exec apache2-foreground\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
