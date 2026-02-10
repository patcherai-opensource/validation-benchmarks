FROM php:8.2-apache

RUN apt-get update && apt-get install -y curl sqlite3 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/lib/app && chown www-data:www-data /var/lib/app

COPY . /var/www/html/
COPY start.sh /usr/local/bin/start.sh

WORKDIR /var/www/html

RUN chmod +x /usr/local/bin/start.sh

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=5s \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/usr/local/bin/start.sh"]
