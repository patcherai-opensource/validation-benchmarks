FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/wiki_platform/app/requirements.txt
RUN pip install -r /var/www/wiki_platform/app/requirements.txt

COPY ./idor_indirect_trading_platform-httpd.conf /etc/apache2/sites-available/wiki_platform-httpd.conf
COPY ./website/wiki_platform.wsgi /var/www/wiki_platform/
COPY ./website/run.py /var/www/wiki_platform/
COPY ./website/app /var/www/wiki_platform/app

# Flag will be provided at runtime via environment variable for K8s compatibility

RUN a2dissite 000-default.conf
RUN a2ensite wiki_platform-httpd.conf
RUN a2enmod headers

# Configure Apache to log to stdout/stderr for K8s compatibility
RUN ln -sf /dev/stdout /var/log/apache2/access.log \
    && ln -sf /dev/stderr /var/log/apache2/error.log

# Suppress server version info
RUN echo "ServerTokens Prod" >> /etc/apache2/apache2.conf \
    && echo "ServerSignature Off" >> /etc/apache2/apache2.conf

CMD  /usr/sbin/apache2ctl -D FOREGROUND
