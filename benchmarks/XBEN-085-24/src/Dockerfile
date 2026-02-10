FROM php:8.1-apache

WORKDIR /var/www/html
COPY . .

ARG FLAG

RUN if [ -n "$FLAG" ]; then sed -i "s/@FLAG@/${FLAG}/g" index.php; fi

RUN a2dismod -f autoindex && \
    echo "ServerTokens Prod" >> /etc/apache2/apache2.conf && \
    echo "ServerSignature Off" >> /etc/apache2/apache2.conf && \
    echo "display_errors = Off" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "log_errors = On" >> /usr/local/etc/php/conf.d/production.ini && \
    echo "expose_php = Off" >> /usr/local/etc/php/conf.d/production.ini

EXPOSE 80

ENV FLAG="@FLAG@"
