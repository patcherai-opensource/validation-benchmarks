FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/artisancms/app/requirements.txt
RUN pip install -r /var/www/artisancms/app/requirements.txt

COPY ./artisancms-httpd.conf /etc/apache2/sites-available/artisancms-httpd.conf
COPY ./website/artisancms.wsgi /var/www/artisancms/
COPY ./website/run.py /var/www/artisancms/
COPY ./website/app /var/www/artisancms/app
RUN chown -R www-data.www-data /var/www/artisancms/app/

RUN a2dissite 000-default.conf
RUN a2ensite artisancms-httpd.conf
RUN a2enmod headers

# Expose port 80 for the web server
EXPOSE 80

# Health check to ensure the service is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

CMD  /usr/sbin/apache2ctl -D FOREGROUND
