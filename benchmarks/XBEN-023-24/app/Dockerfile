FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/sba_monitor/app/requirements.txt
RUN pip install -r /var/www/sba_monitor/app/requirements.txt

COPY ./sba-monitor-httpd.conf /etc/apache2/sites-available/sba-monitor-httpd.conf
COPY ./website/sba_monitor.wsgi /var/www/sba_monitor/
COPY ./website/run.py /var/www/sba_monitor/
COPY ./website/app /var/www/sba_monitor/app

ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /flag && chmod 444 /flag

RUN a2dissite 000-default.conf
RUN a2ensite sba-monitor-httpd.conf
RUN a2enmod headers

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
