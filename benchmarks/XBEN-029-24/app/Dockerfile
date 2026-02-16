FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    php-json \
    php-mbstring \
    mysql-server \
    supervisor \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN a2enmod php7.4 && a2enmod rewrite

COPY website /var/www/html/

WORKDIR /var/www/html/

COPY sitecraft_db.sql /docker-entrypoint-initdb.d/

RUN chown -R mysql:mysql /var/lib/mysql /var/run/mysqld && \
    chmod 777 /var/run/mysqld && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    rm -f /var/www/html/index.html

COPY seed_users.php /tmp/seed_users.php

RUN service mysql start && \
    mysql < /docker-entrypoint-initdb.d/sitecraft_db.sql && \
    php /tmp/seed_users.php && \
    rm /tmp/seed_users.php

# Create media upload directory
RUN mkdir -p /var/www/html/media/uploads && \
    chown -R www-data:www-data /var/www/html/media && \
    chmod -R 775 /var/www/html/media

EXPOSE 80

ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /flag.txt && chmod 444 /flag.txt

COPY apache-sitecraft.conf /etc/apache2/sites-available/000-default.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
