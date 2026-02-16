FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/routerxyz/app/requirements.txt
RUN pip install -r /var/www/routerxyz/app/requirements.txt

COPY ./routerxyz-httpd.conf /etc/apache2/sites-available/routerxyz-httpd.conf
COPY ./website/routerxyz.wsgi /var/www/routerxyz/
COPY ./website/run.py /var/www/routerxyz/
COPY ./website/firmware.cfg /var/www/routerxyz/
COPY ./website/app /var/www/routerxyz/app

ARG FLAG
RUN echo -n ${FLAG:-PLACEHOLDER_FLAG} > /flag
RUN chmod 644 /flag

# Create entrypoint script for runtime flag injection
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint.sh && \
    echo 'if [ -n "$FLAG" ]; then' >> /usr/local/bin/entrypoint.sh && \
    echo '    echo -n "$FLAG" > /flag' >> /usr/local/bin/entrypoint.sh && \
    echo 'fi' >> /usr/local/bin/entrypoint.sh && \
    echo 'exec /usr/sbin/apache2ctl -D FOREGROUND' >> /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

RUN a2dissite 000-default.conf
RUN a2ensite routerxyz-httpd.conf
RUN a2enmod headers

CMD  ["/usr/local/bin/entrypoint.sh"]
