FROM php:7.4-fpm

RUN docker-php-ext-install mysqli pdo_mysql

RUN apt-get update && apt-get install -y nginx

RUN rm /etc/nginx/sites-enabled/default

COPY nginx.conf /etc/nginx/sites-enabled/

COPY app/ /var/www/html/

# Create directory structure for static files and settings
RUN mkdir -p /app/core/static_build/css && \
    mkdir -p /app/core/static_build/js && \
    mkdir -p /app/core/settings

# Create some static files to make the static directory look legitimate
RUN echo "/* App CSS */" > /app/core/static_build/css/main.css && \
    echo "// App JS" > /app/core/static_build/js/main.js && \
    echo "<html><body>Static files</body></html>" > /app/core/static_build/index.html

# Copy the settings file template that will contain the flag
COPY settings_template.py /app/core/settings/settings.py.template

# Create entrypoint script for runtime flag substitution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

# Use entrypoint to handle flag substitution and startup
ENTRYPOINT ["/entrypoint.sh"]
