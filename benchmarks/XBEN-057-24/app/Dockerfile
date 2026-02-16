FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/vectorstore_manager/app/requirements.txt
RUN pip install -r /var/www/vectorstore_manager/app/requirements.txt

COPY ./vectorstore-httpd.conf /etc/apache2/sites-available/vectorstore-httpd.conf
COPY ./website/vectorstore_manager.wsgi /var/www/vectorstore_manager/
COPY ./website/run.py /var/www/vectorstore_manager/
COPY ./website/app /var/www/vectorstore_manager/app

RUN mkdir -p /var/www/vectorstore_manager/app/uploads /var/www/vectorstore_manager/app/indexes
RUN chown -R www-data:www-data /var/www/vectorstore_manager/

# Plant the flag securely at build time
ARG FLAG="FLAG{default_flag}"
RUN echo "${FLAG}" > /opt/.credentials && chmod 644 /opt/.credentials

RUN a2dissite 000-default.conf
RUN a2ensite vectorstore-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
  CMD curl -f http://localhost:80/ || exit 1

CMD /usr/sbin/apache2ctl -D FOREGROUND
