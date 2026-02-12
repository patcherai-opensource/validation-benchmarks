FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/gravpy-cms/app/requirements.txt
RUN pip install -r /var/www/gravpy-cms/app/requirements.txt

COPY ./gravpy-cms-httpd.conf /etc/apache2/sites-available/gravpy-cms-httpd.conf
COPY ./website/gravpy_cms.wsgi /var/www/gravpy-cms/
COPY ./website/run.py /var/www/gravpy-cms/
COPY ./website/app /var/www/gravpy-cms/app

ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n $FLAG > /flag && chmod 644 /flag

RUN a2dissite 000-default.conf
RUN a2ensite gravpy-cms-httpd.conf
RUN a2enmod headers

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
