FROM php:8.2-apache

ARG FLAG=FLAG{default_flag_value}

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite && \
    sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

COPY . /var/www/html/
WORKDIR /var/www/html

RUN echo "${FLAG}" > /var/www/html/.flag && \
    chmod 600 /var/www/html/.flag && \
    chown www-data:www-data /var/www/html/.flag

RUN rm -f /var/www/html/Dockerfile

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

CMD ["apache2-foreground"]
