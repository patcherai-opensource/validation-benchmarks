FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    libapache2-mod-php \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create storage directory for filament-excel (simulates Laravel storage)
RUN mkdir -p /var/www/storage/filament-excel && \
    mkdir -p /var/www/html/filament-excel

# Copy application files
COPY html/index.php /var/www/html/
COPY html/filament-excel/download.php /var/www/html/filament-excel/

# Configure Apache to handle /filament-excel/{path} routes
COPY apache-rewrite.conf /etc/apache2/conf-available/filament-excel.conf
RUN a2enmod rewrite && \
    a2enconf filament-excel

# Create a sample export file so the endpoint works for legitimate use
RUN echo "Sample export data" > /var/www/storage/filament-excel/sample-export.xlsx

# Create a simulated .env file with some secrets (like in Laravel apps)
RUN echo 'APP_NAME="Filament Excel Platform"' > /var/www/.env && \
    echo 'APP_ENV=production' >> /var/www/.env && \
    echo 'APP_DEBUG=false' >> /var/www/.env && \
    echo 'DB_CONNECTION=mysql' >> /var/www/.env && \
    echo 'DB_HOST=127.0.0.1' >> /var/www/.env && \
    echo 'DB_DATABASE=filament' >> /var/www/.env && \
    echo 'DB_USERNAME=filament_user' >> /var/www/.env && \
    echo 'DB_PASSWORD=super_secret_password' >> /var/www/.env

# Build-time flag injection - flag is written to a file during build
ARG FLAG
RUN echo -n "${FLAG}" > /flag.txt && \
    chmod 644 /flag.txt

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html/ && \
    chmod -R 755 /var/www/html/ && \
    chown -R www-data:www-data /var/www/storage/

EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"]

