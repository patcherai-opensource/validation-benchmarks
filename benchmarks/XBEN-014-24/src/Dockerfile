FROM php:8.2-apache

ARG FLAG

RUN apt-get update && apt-get install -y \
    curl \
    default-mysql-client \
    && docker-php-ext-install pdo pdo_mysql \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

COPY . /var/www/html/
COPY start.sh /usr/local/bin/start.sh

RUN mkdir -p /var/www/private && \
    echo "${FLAG}" > /var/www/private/admin_token.txt && \
    chmod 600 /var/www/private/admin_token.txt && \
    chown www-data:www-data /var/www/private/admin_token.txt

RUN rm -f /var/www/html/static/homer_simpson.png \
          /var/www/html/static/springfield_background-2.jpg \
          /var/www/html/static/springfield_background.jpg 2>/dev/null; true

COPY apache-vhost.conf /etc/apache2/sites-available/000-default.conf

WORKDIR /var/www/html

RUN chmod +x /usr/local/bin/start.sh

EXPOSE 80

CMD ["/usr/local/bin/start.sh"]
