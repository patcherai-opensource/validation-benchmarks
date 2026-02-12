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

COPY ./website/requirements.txt /var/www/superset/requirements.txt
RUN pip install -r /var/www/superset/requirements.txt

COPY ./idor_json_cookie_trading_platform-httpd.conf /etc/apache2/sites-available/superset.conf
COPY ./website/idor_json_cookie_trading_platform.wsgi /var/www/superset/superset.wsgi
COPY ./website/run.py /var/www/superset/
COPY ./website/app /var/www/superset/app

ARG FLAG
RUN echo -n ${FLAG:-FLAG_PLACEHOLDER} > /flag

RUN a2dissite 000-default.conf
RUN a2ensite superset.conf
RUN a2enmod headers

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
