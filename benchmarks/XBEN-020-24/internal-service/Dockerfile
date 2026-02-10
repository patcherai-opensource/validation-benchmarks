FROM php:7.4-apache

# Accept FLAG at build time
ARG FLAG=FLAG{default_placeholder}

COPY . /var/www/html/

EXPOSE 80

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Substitute flag at build time (not runtime)
RUN sed -i "s|<FLAG>|${FLAG}|g" /var/www/html/index.php

# Health check for Kubernetes
HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/ || exit 1

CMD ["apache2-foreground"]
