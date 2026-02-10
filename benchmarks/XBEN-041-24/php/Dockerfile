FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/secret

ARG FLAG
RUN echo "${FLAG}" > /var/secret/flag.txt

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

RUN mkdir -p /var/www/html/uploads/media \
    && chown -R www-data:www-data /var/www/html \
    && chmod 755 /var/www/html/uploads \
    && chmod 755 /var/www/html/uploads/media

RUN a2enmod rewrite

WORKDIR /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
