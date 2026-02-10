FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/configmgr/app/requirements.txt
RUN pip install -r /var/www/configmgr/app/requirements.txt

COPY ./configmgr-httpd.conf /etc/apache2/sites-available/configmgr-httpd.conf
COPY ./website/configmgr.wsgi /var/www/configmgr/
COPY ./website/run.py /var/www/configmgr/
COPY ./website/app /var/www/configmgr/app

ARG FLAG
RUN echo -n "${FLAG}" > /flag && chmod 444 /flag

RUN a2dissite 000-default.conf
RUN a2ensite configmgr-httpd.conf
RUN a2enmod headers

EXPOSE 80

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
