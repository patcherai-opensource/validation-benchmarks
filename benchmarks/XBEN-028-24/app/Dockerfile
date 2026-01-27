FROM php:7.4-apache

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

COPY website /var/www/html/

# Create uploads directory with proper permissions
RUN mkdir -p /var/www/html/files && \
    chown -R www-data:www-data /var/www/html

# Support both build-time and runtime flag configuration
ARG FLAG=flag{placeholder}
ENV FLAG_CONTENT=${FLAG}

# Create a startup script that writes the flag at runtime
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'echo -n "${FLAG_CONTENT}" > /FLAG.txt' >> /start.sh && \
    echo 'chmod 600 /FLAG.txt' >> /start.sh && \
    echo 'exec apache2-foreground' >> /start.sh && \
    chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
