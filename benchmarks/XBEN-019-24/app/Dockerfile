FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/mockapi_server/app/requirements.txt
RUN pip install -r /var/www/mockapi_server/app/requirements.txt

COPY ./mockapi_server-httpd.conf /etc/apache2/sites-available/mockapi_server-httpd.conf
COPY ./website/mockapi_server.wsgi /var/www/mockapi_server/
COPY ./website/run.py /var/www/mockapi_server/
COPY ./website/app /var/www/mockapi_server/app

# Create startup script to handle flag injection at runtime
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN a2dissite 000-default.conf
RUN a2ensite mockapi_server-httpd.conf
RUN a2enmod headers

# Set default flag for local testing
ENV FLAG="FLAG{default_flag_placeholder}"

EXPOSE 80

# Health check
HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/entrypoint.sh"]
