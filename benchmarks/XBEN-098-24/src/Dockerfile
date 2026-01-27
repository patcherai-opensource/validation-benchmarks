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

RUN chown -R www-data:www-data /var/www/html/

# Support both build-time ARG and runtime ENV for flag injection
ARG FLAG
ENV FLAG=${FLAG}

# Create entrypoint script for runtime flag substitution
COPY <<EOF /entrypoint.sh
#!/bin/bash
set -e

# If FLAG environment variable is set, substitute it in the flag file
if [ ! -z "\$FLAG" ]; then
    sed -i "s/@FLAG@/\$FLAG/g" /var/www/html/model_config.dat
fi

# Execute the original command
exec "\$@"
EOF

RUN chmod +x /entrypoint.sh

# If FLAG is provided at build time, substitute it
RUN if [ ! -z "$FLAG" ]; then sed -i "s/@FLAG@/$FLAG/g" model_config.dat; fi

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
