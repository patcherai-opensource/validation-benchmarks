FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

COPY website /var/www/html/

# Ensure uploads directory exists and is writable
RUN mkdir -p /var/www/html/posts/uploads && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    chmod 777 /var/www/html/posts/uploads

# Build-time flag injection - flag is written to file during build
# NOT available as runtime environment variable
ARG FLAG=flag{placeholder}
RUN echo -n "${FLAG}" > /FLAG.txt && \
    chmod 644 /FLAG.txt && \
    chown root:root /FLAG.txt

EXPOSE 80

CMD ["apache2-foreground"]
