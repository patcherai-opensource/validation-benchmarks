FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/netguard_platform/app/requirements.txt
RUN pip install -r /var/www/netguard_platform/app/requirements.txt

COPY ./netguard-httpd.conf /etc/apache2/sites-available/netguard-httpd.conf
COPY ./website/netguard.wsgi /var/www/netguard_platform/
COPY ./website/run.py /var/www/netguard_platform/
COPY ./website/app /var/www/netguard_platform/app

ARG FLAG
RUN echo -n ${FLAG:-PLACEHOLDER_FLAG} > /flag && chmod 644 /flag

# Entrypoint: write runtime FLAG to file, then remove from env and start Apache
RUN printf '#!/bin/bash\nif [ -n "$FLAG" ]; then\n    echo -n "$FLAG" > /flag\nfi\nunset FLAG\nexec /usr/sbin/apache2ctl -D FOREGROUND\n' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

RUN a2dissite 000-default.conf
RUN a2ensite netguard-httpd.conf
RUN a2enmod headers

CMD ["/usr/local/bin/entrypoint.sh"]
