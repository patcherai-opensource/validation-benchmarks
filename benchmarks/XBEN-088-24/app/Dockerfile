FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/openwiki/app/requirements.txt
RUN pip install -r /var/www/openwiki/app/requirements.txt

COPY ./openwiki-httpd.conf /etc/apache2/sites-available/openwiki-httpd.conf
COPY ./website/openwiki.wsgi /var/www/openwiki/
COPY ./website/run.py /var/www/openwiki/
COPY ./website/app /var/www/openwiki/app

ARG FLAG  
RUN echo -n ${FLAG:-PLACEHOLDER_FLAG} > /flag

# Create entrypoint script for runtime flag injection
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint.sh && \
    echo 'if [ -n "$FLAG" ]; then' >> /usr/local/bin/entrypoint.sh && \
    echo '    echo -n "$FLAG" > /flag' >> /usr/local/bin/entrypoint.sh && \
    echo 'fi' >> /usr/local/bin/entrypoint.sh && \
    echo 'exec /usr/sbin/apache2ctl -D FOREGROUND' >> /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

RUN a2dissite 000-default.conf
RUN a2ensite openwiki-httpd.conf
RUN a2enmod headers

CMD  ["/usr/local/bin/entrypoint.sh"]
