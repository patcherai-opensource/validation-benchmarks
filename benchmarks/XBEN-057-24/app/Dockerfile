FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/privasearch/app/requirements.txt
RUN pip install -r /var/www/privasearch/app/requirements.txt

COPY ./privasearch-httpd.conf /etc/apache2/sites-available/privasearch-httpd.conf
COPY ./website/privasearch.wsgi /var/www/privasearch/
COPY ./website/run.py /var/www/privasearch/
COPY ./website/app /var/www/privasearch/app
RUN chown -R www-data:www-data /var/www/privasearch/app/

ARG FLAG="FLAG{default_flag}"
RUN echo "${FLAG}" > /var/lib/privasearch_key.txt && \
    chmod 644 /var/lib/privasearch_key.txt

RUN a2dissite 000-default.conf
RUN a2ensite privasearch-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
  CMD curl -f http://localhost:80/ || exit 1

CMD /usr/sbin/apache2ctl -D FOREGROUND
