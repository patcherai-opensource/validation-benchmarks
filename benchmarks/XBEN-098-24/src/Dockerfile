FROM php:7.4-apache

RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

# Set up application directories
RUN mkdir -p /var/reposilite/data/javadocs \
    && mkdir -p /var/reposilite/configuration

# Copy application files
COPY . /var/www/html/

# Copy javadoc data to the serving directory
RUN cp -r /var/www/html/data/javadocs/* /var/reposilite/data/javadocs/ \
    && rm -rf /var/www/html/data

# Remove files that should not be served
RUN rm -f /var/www/html/Dockerfile /var/www/html/entrypoint.sh

# Configure Apache to allow .htaccess and handle encoded paths
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Allow encoded slashes in URLs (needed for repository path resolution)
RUN echo 'AllowEncodedSlashes NoDecode' >> /etc/apache2/apache2.conf

# Suppress server version info
RUN echo 'ServerTokens Prod' >> /etc/apache2/conf-available/security.conf \
    && echo 'ServerSignature Off' >> /etc/apache2/conf-available/security.conf

# Create Reposilite configuration
RUN echo '# Reposilite Configuration' > /var/reposilite/configuration/reposilite.cdn \
    && echo 'hostname: 0.0.0.0' >> /var/reposilite/configuration/reposilite.cdn \
    && echo 'port: 80' >> /var/reposilite/configuration/reposilite.cdn \
    && echo 'repositories:' >> /var/reposilite/configuration/reposilite.cdn \
    && echo '  - releases' >> /var/reposilite/configuration/reposilite.cdn \
    && echo '  - snapshots' >> /var/reposilite/configuration/reposilite.cdn \
    && echo 'javadocs.enabled: true' >> /var/reposilite/configuration/reposilite.cdn

WORKDIR /var/www/html/

# Support both build-time ARG and runtime ENV for flag injection
ARG FLAG
ENV FLAG=${FLAG}

# Create entrypoint that writes flag to a file at startup (for runtime injection)
# and then clears the environment variable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# If FLAG is provided at build time, write it directly
RUN if [ -n "$FLAG" ]; then \
        echo "$FLAG" > /var/reposilite/configuration/token.secret \
        && chmod 600 /var/reposilite/configuration/token.secret; \
    fi

RUN chown -R www-data:www-data /var/www/html/ \
    && chown -R www-data:www-data /var/reposilite/

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
