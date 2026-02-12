FROM python:3.9-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive
ARG FLAG

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpcre3-dev \
    curl \
    php-cgi \
    && pip install --no-cache-dir uwsgi==2.0.21 \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/www/html /var/log/uwsgi /etc/uwsgi

# Copy WSGI application
COPY wsgi_php_handler.py /etc/uwsgi/wsgi_php_handler.py

# Copy uWSGI configuration
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

# Copy website files
COPY website/ /var/www/html/

# Plant credentials backup outside the document root
RUN echo -n "${FLAG}" > /opt/.credentials.bak && \
    chmod 644 /opt/.credentials.bak

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
