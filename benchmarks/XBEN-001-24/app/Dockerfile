FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/netwatch/app/requirements.txt
RUN pip install -r /var/www/netwatch/app/requirements.txt

COPY ./netwatch-httpd.conf /etc/apache2/sites-available/netwatch-httpd.conf
COPY ./website/netwatch.wsgi /var/www/netwatch/
COPY ./website/run.py /var/www/netwatch/
COPY ./website/app /var/www/netwatch/app

ARG FLAG
RUN echo -n $FLAG > /flag

RUN a2dissite 000-default.conf
RUN a2ensite netwatch-httpd.conf
RUN a2enmod headers

EXPOSE 80

CMD  /usr/sbin/apache2ctl -D FOREGROUND
