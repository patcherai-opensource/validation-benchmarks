FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/lunary/app/requirements.txt
RUN pip install -r /var/www/lunary/app/requirements.txt

COPY ./lunary-httpd.conf /etc/apache2/sites-available/lunary-httpd.conf
COPY ./website/lunary.wsgi /var/www/lunary/
COPY ./website/run.py /var/www/lunary/
COPY ./website/app /var/www/lunary/app

RUN a2dissite 000-default.conf
RUN a2ensite lunary-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ping || exit 1

CMD  /usr/sbin/apache2ctl -D FOREGROUND
