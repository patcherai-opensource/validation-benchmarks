FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/service_monitor/app/requirements.txt
RUN pip install -r /var/www/service_monitor/app/requirements.txt

COPY ./service-monitor-httpd.conf /etc/apache2/sites-available/service-monitor-httpd.conf
COPY ./website/service_monitor.wsgi /var/www/service_monitor/
COPY ./website/run.py /var/www/service_monitor/
COPY ./website/app /var/www/service_monitor/app

ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /flag && chmod 644 /flag

RUN a2dissite 000-default.conf
RUN a2ensite service-monitor-httpd.conf
RUN a2enmod headers

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
