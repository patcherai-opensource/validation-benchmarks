FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/gravity-cms/app/requirements.txt
RUN pip install -r /var/www/gravity-cms/app/requirements.txt

COPY ./gravity-cms-httpd.conf /etc/apache2/sites-available/gravity-cms-httpd.conf
COPY ./website/gravity-cms.wsgi /var/www/gravity-cms/
COPY ./website/run.py /var/www/gravity-cms/
COPY ./website/app /var/www/gravity-cms/app

ARG FLAG="PLACEHOLDER_FLAG"
RUN echo -n $FLAG > /flag && chmod 644 /flag

RUN chown -R www-data:www-data /var/www/gravity-cms/
RUN chmod -R 755 /var/www/gravity-cms/

RUN a2dissite 000-default.conf
RUN a2ensite gravity-cms-httpd.conf
RUN a2enmod headers

CMD  /usr/sbin/apache2ctl -D FOREGROUND