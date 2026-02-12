FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl supervisor libcurl4-openssl-dev \
    && docker-php-ext-install mysqli \
    && (docker-php-ext-install curl 2>/dev/null || true) \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf
COPY ./admin-bot.php /opt/admin-bot.php
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/www/html/upload /tmp/telemetry
RUN chown -R www-data:www-data /var/www/html
RUN chmod 777 /tmp/telemetry

WORKDIR /var/www/html

HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=10 \
  CMD curl -f http://localhost/sign-in.php || exit 1

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
