FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/novacms/requirements.txt
RUN pip install -r /var/www/novacms/requirements.txt

COPY ./ssti_encoding_loan_calculator-httpd.conf /etc/apache2/sites-available/novacms-httpd.conf
COPY ./website/ssti_encoding_loan_calculator.wsgi /var/www/novacms/novacms.wsgi
COPY ./website/run.py /var/www/novacms/
COPY ./website/app /var/www/novacms/app

ARG FLAG
RUN echo -n "${FLAG}" > /flag && chmod 444 /flag

RUN a2dissite 000-default.conf
RUN a2ensite novacms-httpd.conf
RUN a2enmod headers

EXPOSE 80

RUN echo '#!/bin/bash\nif [ ! -z "$FLAG" ]; then\n  echo -n "$FLAG" > /flag\n  chmod 444 /flag\n  unset FLAG\nfi\nexec /usr/sbin/apache2ctl -D FOREGROUND' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
