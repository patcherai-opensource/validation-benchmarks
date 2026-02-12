FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/xwiki_platform/app/requirements.txt
RUN pip install -r /var/www/xwiki_platform/app/requirements.txt

COPY ./xwiki-httpd.conf /etc/apache2/sites-available/xwiki-httpd.conf
COPY ./website/xwiki.wsgi /var/www/xwiki_platform/
COPY ./website/run.py /var/www/xwiki_platform/
COPY ./website/app /var/www/xwiki_platform/app

RUN a2dissite 000-default.conf
RUN a2ensite xwiki-httpd.conf
RUN a2enmod headers

RUN ln -sf /dev/stdout /var/log/apache2/access.log \
    && ln -sf /dev/stderr /var/log/apache2/error.log

CMD  /usr/sbin/apache2ctl -D FOREGROUND
