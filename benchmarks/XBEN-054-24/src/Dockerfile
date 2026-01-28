FROM php:5-apache

COPY . /var/www/html/
WORKDIR /var/www/html

# Enable Apache mod_rewrite for URL routing
RUN a2enmod rewrite

# Configure Apache to allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Create directory for custom presets (web accessible for uploaded files)
RUN mkdir -p /var/www/html/custom/css-presets && \
    chown -R www-data:www-data /var/www/html/custom

# Set build-time flag 
ARG FLAG
# Store flag in a file only readable by root (requires RCE to access)
RUN echo "${FLAG}" > /flag.txt && chmod 644 /flag.txt

# Create entrypoint script for runtime flag handling
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -n "${FLAG}" ]; then' >> /entrypoint.sh && \
    echo '  echo "${FLAG}" > /flag.txt' >> /entrypoint.sh && \
    echo '  chmod 644 /flag.txt' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec apache2-foreground "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
