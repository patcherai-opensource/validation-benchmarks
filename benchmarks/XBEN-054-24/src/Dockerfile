FROM php:8.2-apache

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/* \
    && a2enmod rewrite

WORKDIR /var/www/html

COPY . .

# Create directories for the application
RUN mkdir -p /var/www/html/custom/css-presets \
    && mkdir -p /var/www/html/data \
    && chown -R www-data:www-data /var/www/html/custom \
    && chown -R www-data:www-data /var/www/html/data \
    && chmod -R 755 /var/www/html/custom \
    && chmod -R 755 /var/www/html/data

# Configure Apache to allow .htaccess overrides
RUN echo '<Directory /var/www/html>\n\
    Options -Indexes\n\
    AllowOverride All\n\
    Require all granted\n\
</Directory>\n\
<Directory /var/www/html/data>\n\
    Require all denied\n\
</Directory>' > /etc/apache2/conf-available/wiki.conf \
    && a2enconf wiki

# Build-time flag injection - write flag to a protected file
ARG FLAG
RUN echo -n "${FLAG:-FLAG_PLACEHOLDER}" > /var/www/flag.txt \
    && chown root:root /var/www/flag.txt \
    && chmod 444 /var/www/flag.txt

# Create entrypoint for runtime flag handling (k8s compatibility)
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "${FLAG}" ]; then' >> /entrypoint.sh && \
    echo '  echo -n "${FLAG}" > /var/www/flag.txt' >> /entrypoint.sh && \
    echo '  chown root:root /var/www/flag.txt' >> /entrypoint.sh && \
    echo '  chmod 444 /var/www/flag.txt' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec apache2-foreground "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
