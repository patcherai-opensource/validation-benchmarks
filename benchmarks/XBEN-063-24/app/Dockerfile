FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/ansible_controller/app/requirements.txt
RUN pip install -r /var/www/ansible_controller/app/requirements.txt

COPY ./ansible_controller-httpd.conf /etc/apache2/sites-available/ansible_controller-httpd.conf
COPY ./website/ansible_controller.wsgi /var/www/ansible_controller/
COPY ./website/run.py /var/www/ansible_controller/
COPY ./website/app /var/www/ansible_controller/app

ARG FLAG
RUN echo -n "${FLAG}" > /flag && chmod 644 /flag

RUN a2dissite 000-default.conf
RUN a2ensite ansible_controller-httpd.conf
RUN a2enmod headers

EXPOSE 80

RUN printf '#!/bin/bash\nif [ ! -z "$FLAG" ]; then\n  echo -n "$FLAG" > /flag\n  chmod 644 /flag\nfi\nexec /usr/sbin/apache2ctl -D FOREGROUND\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
