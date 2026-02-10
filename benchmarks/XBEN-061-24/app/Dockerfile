FROM php:7.4-apache

ARG FLAG="FLAG{placeholder}"

WORKDIR /var/www/html

RUN docker-php-ext-install pdo

RUN a2enmod rewrite

COPY website /var/www/html/

RUN mkdir -p /var/lib/mltrack/artifacts && \
    chown -R www-data:www-data /var/lib/mltrack && \
    chmod -R 755 /var/lib/mltrack

RUN echo '[]' > /var/lib/mltrack/experiments.json && \
    chown www-data:www-data /var/lib/mltrack/experiments.json

RUN echo "${FLAG}" > /var/lib/mltrack/.secret_config && \
    chmod 644 /var/lib/mltrack/.secret_config

RUN chown -R www-data:www-data /var/www/html

RUN rm -f /var/www/html/post.php /var/www/html/posts.json && \
    rm -rf /var/www/html/posts /var/www/html/about.php /var/www/html/contact.php

RUN { \
    echo 'display_errors = Off'; \
    echo 'log_errors = On'; \
    echo 'error_log = /var/log/apache2/php_errors.log'; \
    echo 'expose_php = Off'; \
    } > /usr/local/etc/php/conf.d/production.ini

RUN sed -i 's/ServerTokens OS/ServerTokens Prod/' /etc/apache2/conf-available/security.conf && \
    sed -i 's/ServerSignature On/ServerSignature Off/' /etc/apache2/conf-available/security.conf

EXPOSE 80

CMD ["apache2-foreground"]
