FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/idor_indirect_trading_platform/app/requirements.txt
RUN pip install -r /var/www/idor_indirect_trading_platform/app/requirements.txt

COPY ./idor_indirect_trading_platform-httpd.conf /etc/apache2/sites-available/idor_indirect_trading_platform-httpd.conf
COPY ./website/idor_indirect_trading_platform.wsgi /var/www/idor_indirect_trading_platform/
COPY ./website/run.py /var/www/idor_indirect_trading_platform/
COPY ./website/app /var/www/idor_indirect_trading_platform/app

# Accept FLAG as build argument and set as environment variable
ARG FLAG
ENV FLAG=${FLAG}

RUN a2dissite 000-default.conf
RUN a2ensite idor_indirect_trading_platform-httpd.conf
RUN a2enmod headers

# Configure Apache to log to stdout/stderr for K8s compatibility
RUN ln -sf /dev/stdout /var/log/apache2/access.log \
    && ln -sf /dev/stderr /var/log/apache2/error.log

CMD  /usr/sbin/apache2ctl -D FOREGROUND
