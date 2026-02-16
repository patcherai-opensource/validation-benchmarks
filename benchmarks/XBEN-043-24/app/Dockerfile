FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/contentflow/app/requirements.txt
RUN pip install -r /var/www/contentflow/app/requirements.txt

COPY ./contentflow-httpd.conf /etc/apache2/sites-available/contentflow-httpd.conf
COPY ./website/contentflow.wsgi /var/www/contentflow/
COPY ./website/run.py /var/www/contentflow/
COPY ./website/app /var/www/contentflow/app

RUN a2dissite 000-default.conf
RUN a2ensite contentflow-httpd.conf
RUN a2enmod headers

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
