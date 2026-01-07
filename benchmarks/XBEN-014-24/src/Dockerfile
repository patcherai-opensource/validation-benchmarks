FROM php:8.2-apache

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . /var/www/html/
COPY start.sh /usr/local/bin/start.sh

WORKDIR /var/www/html

RUN chmod +x /usr/local/bin/start.sh

EXPOSE 80

# Health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=5s \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/usr/local/bin/start.sh"]
