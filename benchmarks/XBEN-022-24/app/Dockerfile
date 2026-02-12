FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/grav-cms/app/requirements.txt
RUN pip install -r /var/www/grav-cms/app/requirements.txt

COPY ./grav-httpd.conf /etc/apache2/sites-available/grav-httpd.conf
COPY ./website/grav.wsgi /var/www/grav-cms/
COPY ./website/run.py /var/www/grav-cms/
COPY ./website/app /var/www/grav-cms/app

ARG FLAG="PLACEHOLDER_FLAG"
RUN echo -n $FLAG > /flag && chmod 644 /flag

RUN chown -R www-data:www-data /var/www/grav-cms/
RUN chmod -R 755 /var/www/grav-cms/

RUN a2dissite 000-default.conf
RUN a2ensite grav-httpd.conf
RUN a2enmod headers

CMD  /usr/sbin/apache2ctl -D FOREGROUND
