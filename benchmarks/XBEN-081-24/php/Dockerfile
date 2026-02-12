FROM php:8.2-apache

RUN docker-php-ext-install mysqli

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Disable PHP expose and error display for production
RUN echo "expose_php = Off" > /usr/local/etc/php/conf.d/security.ini \
    && echo "display_errors = Off" >> /usr/local/etc/php/conf.d/security.ini \
    && echo "log_errors = On" >> /usr/local/etc/php/conf.d/security.ini \
    && echo "error_log = /var/log/php_errors.log" >> /usr/local/etc/php/conf.d/security.ini

# Disable Apache server tokens
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security.conf

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

RUN chown -R www-data:www-data /var/www/html

WORKDIR /var/www/html

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
  CMD curl -f http://localhost/store/ || exit 1

EXPOSE 80
