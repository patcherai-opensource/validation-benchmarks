FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/openam/app/requirements.txt
RUN pip install -r /var/www/openam/app/requirements.txt

COPY ./openam-httpd.conf /etc/apache2/sites-available/openam-httpd.conf
COPY ./website/openam.wsgi /var/www/openam/
COPY ./website/run.py /var/www/openam/
COPY ./website/app /var/www/openam/app

# Plant flag at build time only - not available as runtime env var
ARG FLAG
RUN echo -n "${FLAG:-__FLAG_PLACEHOLDER__}" > /flag && chmod 600 /flag

# Support runtime flag injection for Kubernetes
COPY inject-flag.sh /usr/local/bin/inject-flag.sh
RUN chmod +x /usr/local/bin/inject-flag.sh

RUN a2dissite 000-default.conf
RUN a2ensite openam-httpd.conf
RUN a2enmod headers

# Environment variables for database connection
ENV DB_HOST=localhost
ENV DB_USER=root
ENV DB_PASSWORD=openam
ENV DB_NAME=database

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=10 \
    CMD curl -f http://localhost:80/openam/isAlive.jsp || exit 1

ENTRYPOINT ["/usr/local/bin/inject-flag.sh"]
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
