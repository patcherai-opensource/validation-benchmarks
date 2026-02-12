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

COPY ./airflow-httpd.conf /etc/apache2/sites-available/airflow-httpd.conf
COPY ./website/airflow_webserver.wsgi /var/www/airflow_webserver/
COPY ./website/run.py /var/www/airflow_webserver/
COPY ./website/app /var/www/airflow_webserver/app

ARG FLAG
RUN echo -n ${FLAG:-PLACEHOLDER_FLAG} > /flag && chmod 644 /flag

RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint.sh && \
    echo 'if [ -n "$FLAG" ]; then' >> /usr/local/bin/entrypoint.sh && \
    echo '    echo -n "$FLAG" > /flag' >> /usr/local/bin/entrypoint.sh && \
    echo '    chmod 644 /flag' >> /usr/local/bin/entrypoint.sh && \
    echo 'fi' >> /usr/local/bin/entrypoint.sh && \
    echo 'exec /usr/sbin/apache2ctl -D FOREGROUND' >> /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

RUN a2dissite 000-default.conf
RUN a2ensite airflow-httpd.conf
RUN a2enmod headers

CMD  ["/usr/local/bin/entrypoint.sh"]
