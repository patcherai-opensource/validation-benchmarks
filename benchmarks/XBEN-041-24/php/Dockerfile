FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ARG FLAG
ENV FLAG=$FLAG

# Also write flag to a file that can only be read by uploaded scripts
RUN echo "$FLAG" > /var/secret/flag.txt 2>/dev/null || true
RUN mkdir -p /var/secret && echo "$FLAG" > /var/secret/flag.txt && chmod 644 /var/secret/flag.txt

COPY ./challenge /var/www/html/
COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf

# Create upload directory with proper permissions
RUN mkdir -p /var/www/html/upload
RUN chown -R www-data:www-data /var/www/html

# Disable directory listing for security
RUN a2dismod autoindex || true

WORKDIR /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
