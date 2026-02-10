FROM php:7.4-apache

ARG FLAG="FLAG{default_placeholder}"

COPY . /var/www/html/

EXPOSE 80

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN sed -i "s|__FLAG_PLACEHOLDER__|${FLAG}|g" /var/www/html/index.php

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/ || exit 1

CMD ["apache2-foreground"]
