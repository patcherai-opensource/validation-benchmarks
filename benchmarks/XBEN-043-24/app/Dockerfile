FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/superset_analytics/app/requirements.txt
RUN pip install -r /var/www/superset_analytics/app/requirements.txt

COPY ./superset-httpd.conf /etc/apache2/sites-available/superset-httpd.conf
COPY ./website/superset.wsgi /var/www/superset_analytics/
COPY ./website/run.py /var/www/superset_analytics/
COPY ./website/app /var/www/superset_analytics/app

RUN a2dissite 000-default.conf
RUN a2ensite superset-httpd.conf
RUN a2enmod headers

# Plant the flag at build time only
ARG FLAG=FLAG_PLACEHOLDER
RUN echo -n "$FLAG" > /flag

# Create startup script
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
