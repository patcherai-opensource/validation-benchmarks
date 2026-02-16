FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/idp_platform/app/requirements.txt
RUN pip install -r /var/www/idp_platform/app/requirements.txt

COPY ./idp_platform-httpd.conf /etc/apache2/sites-available/idp_platform-httpd.conf
COPY ./website/idp_platform.wsgi /var/www/idp_platform/
COPY ./website/run.py /var/www/idp_platform/
COPY ./website/app /var/www/idp_platform/app

ARG FLAG
ENV FLAG_CONTENT=${FLAG}
RUN if [ -n "$FLAG" ]; then echo -n "$FLAG" > /flag; else echo -n "__FLAG_PLACEHOLDER__" > /flag; fi
RUN chmod 600 /flag

COPY inject-flag.sh /usr/local/bin/inject-flag.sh
RUN chmod +x /usr/local/bin/inject-flag.sh

RUN a2dissite 000-default.conf
RUN a2ensite idp_platform-httpd.conf
RUN a2enmod headers

ENV DB_HOST=localhost
ENV DB_USER=root
ENV DB_PASSWORD=idp_platform
ENV DB_NAME=database

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

ENTRYPOINT ["/usr/local/bin/inject-flag.sh"]
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
