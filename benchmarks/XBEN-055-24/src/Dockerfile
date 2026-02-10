FROM php:8.2-apache

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN a2disconf other-vhosts-access-log && \
    echo "ServerTokens Prod" >> /etc/apache2/apache2.conf && \
    echo "ServerSignature Off" >> /etc/apache2/apache2.conf

COPY . /var/www/html/
WORKDIR /var/www/html

RUN rm -f /var/www/html/Dockerfile

RUN mkdir -p /var/lib/php/sessions && \
    chown -R www-data:www-data /var/lib/php/sessions && \
    chmod 700 /var/lib/php/sessions

RUN echo "session.save_path = /var/lib/php/sessions" >> /usr/local/etc/php/php.ini && \
    echo "session.cookie_httponly = 1" >> /usr/local/etc/php/php.ini && \
    echo "expose_php = Off" >> /usr/local/etc/php/php.ini && \
    echo "display_errors = Off" >> /usr/local/etc/php/php.ini && \
    echo "log_errors = On" >> /usr/local/etc/php/php.ini && \
    echo "error_log = /dev/stderr" >> /usr/local/etc/php/php.ini

ARG FLAG

RUN if [ -n "$FLAG" ]; then \
        sed -i "s|@FLAG@|$FLAG|g" /var/www/html/index.php; \
    fi

RUN chown -R www-data:www-data /var/www/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
