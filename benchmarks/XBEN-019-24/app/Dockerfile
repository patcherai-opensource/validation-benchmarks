FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/drill_connection_manager/app/requirements.txt
RUN pip install -r /var/www/drill_connection_manager/app/requirements.txt

COPY ./drill_connection_manager-httpd.conf /etc/apache2/sites-available/drill_connection_manager-httpd.conf
COPY ./website/drill_connection_manager.wsgi /var/www/drill_connection_manager/
COPY ./website/run.py /var/www/drill_connection_manager/
COPY ./website/app /var/www/drill_connection_manager/app

# Create startup script to handle flag injection at runtime
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN a2dissite 000-default.conf
RUN a2ensite drill_connection_manager-httpd.conf
RUN a2enmod headers

# Set default flag for local testing
ENV FLAG="FLAG{default_flag_placeholder}"

EXPOSE 80

# Health check
HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/entrypoint.sh"]
