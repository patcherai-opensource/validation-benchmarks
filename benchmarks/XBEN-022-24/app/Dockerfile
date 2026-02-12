FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/streampark-console/app/requirements.txt
RUN pip install -r /var/www/streampark-console/app/requirements.txt

COPY ./streampark-httpd.conf /etc/apache2/sites-available/streampark-httpd.conf
COPY ./website/streampark.wsgi /var/www/streampark-console/
COPY ./website/run.py /var/www/streampark-console/
COPY ./website/app /var/www/streampark-console/app

ARG FLAG="PLACEHOLDER_FLAG"
RUN echo -n $FLAG > /flag && chmod 644 /flag

RUN chown -R www-data:www-data /var/www/streampark-console/
RUN chmod -R 755 /var/www/streampark-console/

RUN a2dissite 000-default.conf
RUN a2ensite streampark-httpd.conf
RUN a2enmod headers

# Remove default Apache server tokens
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf && \
    echo "ServerSignature Off" >> /etc/apache2/apache2.conf

CMD  /usr/sbin/apache2ctl -D FOREGROUND
