FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/reportgen/app/requirements.txt
RUN pip install -r /var/www/reportgen/app/requirements.txt

COPY ./reportgen-httpd.conf /etc/apache2/sites-available/reportgen-httpd.conf
COPY ./website/reportgen.wsgi /var/www/reportgen/
COPY ./website/run.py /var/www/reportgen/
COPY ./website/app /var/www/reportgen/app

ARG FLAG
ENV FLAG=${FLAG}
RUN echo -n "${FLAG}" > /flag.txt

RUN a2dissite 000-default.conf
RUN a2ensite reportgen-httpd.conf
RUN a2enmod headers

# Expose port 80
EXPOSE 80

# Create entrypoint script to handle flag injection at runtime
RUN echo '#!/bin/bash\nif [ ! -z "$FLAG" ]; then\n  echo -n "$FLAG" > /flag.txt\nfi\nexec /usr/sbin/apache2ctl -D FOREGROUND' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
