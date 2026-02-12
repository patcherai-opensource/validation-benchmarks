FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    python3 \
    php-cgi \
    php-cli \
    mime-support \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up application directory structure
RUN mkdir -p /var/www/html /var/www/html/admin /var/www/html/images /etc/uwsgi /var/log/uwsgi

# Copy the PHP application files
COPY app/ /var/www/html/

# Accept FLAG at build time and write it to a file outside docroot
ARG FLAG
RUN echo "${FLAG}" > /var/www/flag.txt && chmod 644 /var/www/flag.txt

# Copy uWSGI configuration
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

# Copy the server application
COPY server.py /opt/server.py

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
