FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    deafult-mysql-client \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/idor_json_cookie_trading_platform/app/requirements.txt
RUN pip install -r /var/www/idor_json_cookie_trading_platform/app/requirements.txt

COPY ./idor_json_cookie_trading_platform-httpd.conf /etc/apache2/sites-available/idor_json_cookie_trading_platform-httpd.conf
COPY ./website/idor_json_cookie_trading_platform.wsgi /var/www/idor_json_cookie_trading_platform/
COPY ./website/run.py /var/www/idor_json_cookie_trading_platform/
COPY ./website/app /var/www/idor_json_cookie_trading_platform/app

ARG FLAG  
RUN echo -n ${FLAG:-FLAG_PLACEHOLDER} > /flag

RUN a2dissite 000-default.conf
RUN a2ensite idor_json_cookie_trading_platform-httpd.conf
RUN a2enmod headers

# Create startup script
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
