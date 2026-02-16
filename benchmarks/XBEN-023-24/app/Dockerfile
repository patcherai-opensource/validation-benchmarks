FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/dataflow_console/app/requirements.txt
RUN pip install -r /var/www/dataflow_console/app/requirements.txt

COPY ./dataflow-console-httpd.conf /etc/apache2/sites-available/dataflow-console-httpd.conf
COPY ./website/dataflow_console.wsgi /var/www/dataflow_console/
COPY ./website/run.py /var/www/dataflow_console/
COPY ./website/app /var/www/dataflow_console/app

ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /flag && chmod 644 /flag

RUN a2dissite 000-default.conf
RUN a2ensite dataflow-console-httpd.conf
RUN a2enmod headers

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
