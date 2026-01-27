FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/cloudconfig/app/requirements.txt
RUN pip install -r /var/www/cloudconfig/app/requirements.txt

COPY ./cloudconfig-httpd.conf /etc/apache2/sites-available/cloudconfig-httpd.conf
COPY ./website/cloudconfig.wsgi /var/www/cloudconfig/
COPY ./website/run.py /var/www/cloudconfig/
COPY ./website/app /var/www/cloudconfig/app

RUN a2dissite 000-default.conf
RUN a2ensite cloudconfig-httpd.conf
RUN a2enmod headers

# Expose port 80 for K8s service mapping
EXPOSE 80

# Health check for K8s readiness/liveness probes
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

CMD  /usr/sbin/apache2ctl -D FOREGROUND
