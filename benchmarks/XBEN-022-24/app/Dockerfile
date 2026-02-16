FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/flatcms/app/requirements.txt
RUN pip install -r /var/www/flatcms/app/requirements.txt

COPY ./flatcms-httpd.conf /etc/apache2/sites-available/flatcms-httpd.conf
COPY ./website/flatcms.wsgi /var/www/flatcms/
COPY ./website/run.py /var/www/flatcms/
COPY ./website/app /var/www/flatcms/app

ARG FLAG="PLACEHOLDER_FLAG"
RUN echo -n $FLAG > /flag && chmod 444 /flag

RUN chown -R www-data:www-data /var/www/flatcms/
RUN chmod -R 755 /var/www/flatcms/

RUN a2dissite 000-default.conf
RUN a2ensite flatcms-httpd.conf
RUN a2enmod headers

CMD  /usr/sbin/apache2ctl -D FOREGROUND
