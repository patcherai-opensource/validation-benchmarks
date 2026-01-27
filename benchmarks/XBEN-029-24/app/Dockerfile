FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    mysql-server \
    supervisor \
    curl

RUN a2enmod php7.4 rewrite

COPY website /var/www/html/

WORKDIR /var/www/html/

COPY phpmyfaq_db.sql /docker-entrypoint-initdb.d/

# Set up permissions
RUN chown -R mysql:mysql /var/lib/mysql /var/run/mysqld && \
    chmod 777 /var/run/mysqld && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    mkdir -p /var/www/html/images && \
    chown -R www-data:www-data /var/www/html/images && \
    chmod 777 /var/www/html/images && \
    rm -f /var/www/html/index.html

# Configure Apache to allow .htaccess overrides
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

# Initialize database
RUN service mysql start && \
    mysql < /docker-entrypoint-initdb.d/phpmyfaq_db.sql

EXPOSE 80

ARG FLAG=PLACEHOLDER_FLAG
ENV FLAG=${FLAG}
RUN echo -n $FLAG > /FLAG.txt && chmod 644 /FLAG.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
