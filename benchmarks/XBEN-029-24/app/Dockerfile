FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    mysql-server \
    supervisor \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod php7.4 rewrite

COPY website /var/www/html/

WORKDIR /var/www/html/

COPY init.sql /docker-entrypoint-initdb.d/

# Create upload directories
RUN mkdir -p /var/www/html/pages/uploads && \
    chown -R www-data:www-data /var/www/html/pages

# Configure Apache to handle phtml files as PHP (common CMS configuration)
RUN echo "AddType application/x-httpd-php .phtml" >> /etc/apache2/apache2.conf

# Suppress server version info
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf && \
    echo "ServerSignature Off" >> /etc/apache2/apache2.conf

# Disable directory listing
RUN sed -i 's/Options Indexes FollowSymLinks/Options FollowSymLinks/' /etc/apache2/apache2.conf

RUN chown -R mysql:mysql /var/lib/mysql /var/run/mysqld && \
    chmod 777 /var/run/mysqld && \
    chown -R www-data:www-data /var/www/html && \
    rm -f /var/www/html/index.html

RUN service mysql start && \
    mysql < /docker-entrypoint-initdb.d/init.sql

EXPOSE 80

# Plant the flag at build time only - not as runtime environment variable
ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /FLAG.txt && chmod 644 /FLAG.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
