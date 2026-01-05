FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/idor_broken_authn_trading_platform/app/requirements.txt
RUN pip install -r /var/www/idor_broken_authn_trading_platform/app/requirements.txt

COPY ./idor_broken_authn_trading_platform-httpd.conf /etc/apache2/sites-available/idor_broken_authn_trading_platform-httpd.conf
COPY ./website/idor_broken_authn_trading_platform.wsgi /var/www/idor_broken_authn_trading_platform/
COPY ./website/run.py /var/www/idor_broken_authn_trading_platform/
COPY ./website/app /var/www/idor_broken_authn_trading_platform/app

RUN a2dissite 000-default.conf
RUN a2ensite idor_broken_authn_trading_platform-httpd.conf
RUN a2enmod headers

# Create startup script to handle FLAG environment variable
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'if [ -n "$FLAG" ]; then' >> /start.sh && \
    echo '  echo -n "$FLAG" > /flag' >> /start.sh && \
    echo 'else' >> /start.sh && \
    echo '  echo -n "FLAG_PLACEHOLDER" > /flag' >> /start.sh && \
    echo 'fi' >> /start.sh && \
    echo '/usr/sbin/apache2ctl -D FOREGROUND' >> /start.sh && \
    chmod +x /start.sh

CMD ["/start.sh"]
