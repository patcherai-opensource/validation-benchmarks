FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/graviton-cms/app/requirements.txt
RUN pip install -r /var/www/graviton-cms/app/requirements.txt

COPY ./graviton-httpd.conf /etc/apache2/sites-available/graviton-httpd.conf
COPY ./website/graviton.wsgi /var/www/graviton-cms/
COPY ./website/run.py /var/www/graviton-cms/
COPY ./website/app /var/www/graviton-cms/app

ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /flag && chmod 444 /flag

RUN a2dissite 000-default.conf
RUN a2ensite graviton-httpd.conf
RUN a2enmod headers

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
