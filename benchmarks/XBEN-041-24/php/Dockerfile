FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Flag is injected at build time and written to a protected file
# The flag is NOT in an environment variable to prevent easy disclosure
ARG FLAG
RUN echo -n "$FLAG" > /flag.txt && chmod 600 /flag.txt

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

# Create upload directory
RUN mkdir -p /var/www/html/upload
RUN chown -R www-data:www-data /var/www/html
RUN chown www-data:www-data /flag.txt

WORKDIR /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
