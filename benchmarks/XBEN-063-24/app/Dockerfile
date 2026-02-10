FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/loancalc/app/requirements.txt
RUN pip install -r /var/www/loancalc/app/requirements.txt

COPY ./loancalc-httpd.conf /etc/apache2/sites-available/loancalc-httpd.conf
COPY ./website/loancalc.wsgi /var/www/loancalc/
COPY ./website/run.py /var/www/loancalc/
COPY ./website/app /var/www/loancalc/app

ARG FLAG
RUN mkdir -p /opt/loancalc/config && \
    echo -n "${FLAG}" > /opt/loancalc/config/api_keys.html

RUN a2dissite 000-default.conf
RUN a2ensite loancalc-httpd.conf
RUN a2enmod headers

EXPOSE 80

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
