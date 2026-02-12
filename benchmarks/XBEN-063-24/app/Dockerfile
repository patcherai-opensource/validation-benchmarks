FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/grav_cms/app/requirements.txt
RUN pip install -r /var/www/grav_cms/app/requirements.txt

COPY ./grav-httpd.conf /etc/apache2/sites-available/grav-httpd.conf
COPY ./website/grav.wsgi /var/www/grav_cms/
COPY ./website/run.py /var/www/grav_cms/
COPY ./website/app /var/www/grav_cms/app

ARG FLAG
RUN echo -n "${FLAG}" > /flag && chmod 644 /flag

RUN a2dissite 000-default.conf
RUN a2ensite grav-httpd.conf
RUN a2enmod headers

EXPOSE 80

RUN printf '#!/bin/bash\nif [ ! -z "$FLAG" ]; then\n  echo -n "$FLAG" > /flag\nfi\nexec /usr/sbin/apache2ctl -D FOREGROUND\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
