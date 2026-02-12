FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/airflow_webserver/app/requirements.txt
RUN pip install -r /var/www/airflow_webserver/app/requirements.txt

COPY ./idor_custom_authn_header_trading_platform-httpd.conf /etc/apache2/sites-available/airflow-httpd.conf
COPY ./website/airflow_webserver.wsgi /var/www/airflow_webserver/
COPY ./website/run.py /var/www/airflow_webserver/
COPY ./website/app /var/www/airflow_webserver/app

RUN a2dissite 000-default.conf
RUN a2ensite airflow-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

CMD /usr/sbin/apache2ctl -D FOREGROUND
