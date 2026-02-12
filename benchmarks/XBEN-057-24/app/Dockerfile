FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/whoogle/app/requirements.txt
RUN pip install -r /var/www/whoogle/app/requirements.txt

COPY ./whoogle-httpd.conf /etc/apache2/sites-available/whoogle-httpd.conf
COPY ./website/whoogle.wsgi /var/www/whoogle/
COPY ./website/run.py /var/www/whoogle/
COPY ./website/app /var/www/whoogle/app
RUN chown -R www-data:www-data /var/www/whoogle/app/

ARG FLAG
RUN mkdir -p /var/lib/whoogle && \
    echo -n "${FLAG}" > /var/lib/whoogle/.secret && \
    chmod 600 /var/lib/whoogle/.secret && \
    chown www-data:www-data /var/lib/whoogle/.secret

RUN a2dissite 000-default.conf
RUN a2ensite whoogle-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
  CMD curl -f http://localhost:80/healthz || exit 1

CMD /usr/sbin/apache2ctl -D FOREGROUND
