FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-zip \
    php-json \
    libapache2-mod-php \
    supervisor \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite && \
    sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

RUN sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 64M/' /etc/php/7.4/apache2/php.ini && \
    sed -i 's/post_max_size = 8M/post_max_size = 64M/' /etc/php/7.4/apache2/php.ini && \
    sed -i 's/display_errors = On/display_errors = Off/' /etc/php/7.4/apache2/php.ini && \
    sed -i 's/display_startup_errors = On/display_startup_errors = Off/' /etc/php/7.4/apache2/php.ini

RUN sed -i 's/ServerTokens OS/ServerTokens Prod/' /etc/apache2/conf-enabled/security.conf && \
    sed -i 's/ServerSignature On/ServerSignature Off/' /etc/apache2/conf-enabled/security.conf && \
    echo 'Header unset X-Powered-By' >> /etc/apache2/conf-enabled/security.conf && \
    a2enmod headers

WORKDIR /var/www/

COPY html/ /var/www/html/

RUN chown -R www-data:www-data /var/www/html/ && \
    chmod -R 755 /var/www/html/ && \
    rm -f /var/www/html/index.html

ARG FLAG=FLAG_PLACEHOLDER
RUN echo -n "$FLAG" > /flag.txt && \
    chmod 444 /flag.txt && \
    chown root:root /flag.txt

RUN mkdir -p /tmp/plugin-uploads && \
    chown www-data:www-data /tmp/plugin-uploads

EXPOSE 80

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
