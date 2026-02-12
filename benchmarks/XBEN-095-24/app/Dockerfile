FROM php:7.4-apache

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install mysqli pdo pdo_mysql

# Enable Apache mod_rewrite for clean URLs
RUN a2enmod rewrite

WORKDIR /var/www/html/

COPY . /var/www/html/

# Configure Apache for XWiki-like URL routing
RUN echo '<Directory /var/www/html>\n\
    AllowOverride All\n\
    Require all granted\n\
</Directory>' > /etc/apache2/conf-available/xwiki.conf \
    && a2enconf xwiki \
    && sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

# Remove server signature/version info
RUN echo 'ServerTokens Prod' >> /etc/apache2/apache2.conf \
    && echo 'ServerSignature Off' >> /etc/apache2/apache2.conf

RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
CMD ["apache2-foreground"]
