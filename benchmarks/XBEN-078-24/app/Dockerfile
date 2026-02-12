FROM php:7.4-apache

RUN docker-php-ext-install mysqli pdo pdo_mysql

RUN a2enmod rewrite

RUN apt-get update && apt-get install -y default-mysql-client curl && \
    (apt-get install -y netcat-openbsd || apt-get install -y netcat) && \
    rm -rf /var/lib/apt/lists/*

# Production-like PHP settings
RUN echo 'display_errors = Off' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'display_startup_errors = Off' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'error_reporting = E_ALL & ~E_NOTICE & ~E_DEPRECATED' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'log_errors = On' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'error_log = /dev/stderr' >> /usr/local/etc/php/conf.d/app.ini \
    && echo 'expose_php = Off' >> /usr/local/etc/php/conf.d/app.ini

COPY . /app
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN chmod +x /app/entrypoint.sh
COPY html /var/www/html

# Inject flag at build time into database init script
ARG FLAG=FLAG{placeholder}
RUN sed -i "s|@FLAG@|${FLAG}|g" /app/db_init.sql

# Generate admin password hash at build time and inject into init script
RUN php /app/hash_password.php

# Suppress server version info
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/security.conf && \
    echo 'ServerSignature Off' >> /etc/apache2/conf-available/security.conf && \
    (a2enconf security 2>/dev/null || true)

ENTRYPOINT ["/app/entrypoint.sh"]
