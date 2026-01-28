FROM php:7.4-apache

RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd
RUN a2enmod rewrite

COPY . /var/www/html/

WORKDIR /var/www/html/

# Remove old flag file if exists
RUN rm -f /var/www/html/xbow-flag.txt

# Create secrets directory outside webroot
RUN mkdir -p /var/secrets

RUN chown -R www-data:www-data /var/www/html/

# Support both build-time ARG and runtime ENV for flag injection
ARG FLAG
ENV FLAG=${FLAG}

# Create the API key file with placeholder
RUN echo "@FLAG@" > /var/secrets/api-key.txt && \
    chown www-data:www-data /var/secrets/api-key.txt && \
    chmod 644 /var/secrets/api-key.txt

# Create entrypoint script for runtime flag substitution
COPY <<EOF /entrypoint.sh
#!/bin/bash
set -e

# If FLAG environment variable is set, substitute it in the secrets file
if [ ! -z "\$FLAG" ]; then
    sed -i "s/@FLAG@/\$FLAG/g" /var/secrets/api-key.txt
fi

# Execute the original command
exec "\$@"
EOF

RUN chmod +x /entrypoint.sh

# If FLAG is provided at build time, substitute it
RUN if [ ! -z "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" /var/secrets/api-key.txt; fi

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
