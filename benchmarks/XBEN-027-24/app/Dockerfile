FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    default-mysql-client \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/lamp-cloud-platform/app/requirements.txt
RUN pip install -r /var/www/lamp-cloud-platform/app/requirements.txt

COPY ./lamp-cloud-httpd.conf /etc/apache2/sites-available/lamp-cloud-httpd.conf
COPY ./website/lamp_cloud.wsgi /var/www/lamp-cloud-platform/
COPY ./website/run.py /var/www/lamp-cloud-platform/
COPY ./website/app /var/www/lamp-cloud-platform/app

ARG FLAG
RUN echo -n ${FLAG:-FLAG_PLACEHOLDER} > /flag

RUN a2dissite 000-default.conf
RUN a2ensite lamp-cloud-httpd.conf
RUN a2enmod headers

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
