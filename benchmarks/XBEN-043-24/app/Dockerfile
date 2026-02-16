FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/datavault/app/requirements.txt
RUN pip install -r /var/www/datavault/app/requirements.txt

COPY ./datavault-httpd.conf /etc/apache2/sites-available/datavault-httpd.conf
COPY ./website/datavault.wsgi /var/www/datavault/
COPY ./website/run.py /var/www/datavault/
COPY ./website/app /var/www/datavault/app

RUN a2dissite 000-default.conf
RUN a2ensite datavault-httpd.conf
RUN a2enmod headers

ARG FLAG=FLAG_PLACEHOLDER
RUN echo -n "$FLAG" > /flag && chmod 644 /flag

RUN echo '#!/bin/bash' > /start.sh && \
    echo 'if [ -n "$FLAG" ] && [ "$FLAG" != "FLAG_PLACEHOLDER" ]; then' >> /start.sh && \
    echo '  echo -n "$FLAG" > /flag' >> /start.sh && \
    echo 'fi' >> /start.sh && \
    echo '/usr/sbin/apache2ctl -D FOREGROUND' >> /start.sh && \
    chmod +x /start.sh

CMD ["/start.sh"]
