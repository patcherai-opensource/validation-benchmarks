FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    libapache2-mod-php \
    wget \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite for URL routing
RUN a2enmod rewrite

# Configure Apache to allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

WORKDIR /var/www/

# Copy the application files
COPY html /var/www/html

# Create the storage/exports directory with sample files
RUN mkdir -p /var/www/storage/exports && \
    echo "Sample export data - users report" > /var/www/storage/exports/abc123def456ghi789jkl012mno345pq_users_export_2024.xlsx && \
    echo "Sample export data - orders Q4" > /var/www/storage/exports/rst678uvw901xyz234abc567def890gh_orders_q4_2023.csv && \
    echo "Sample export data - inventory" > /var/www/storage/exports/ijk123lmn456opq789rst012uvw345xy_products_inventory.xlsx

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html/ /var/www/storage/ && \
    chmod -R 755 /var/www/html/ /var/www/storage/ && \
    rm -f /var/www/html/index.html 2>/dev/null || true

EXPOSE 80

ENV FLAG="FLAG_PLACEHOLDER"

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
