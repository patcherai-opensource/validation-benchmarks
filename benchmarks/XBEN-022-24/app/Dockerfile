FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/translation_cms/app/requirements.txt
RUN pip install -r /var/www/translation_cms/app/requirements.txt

COPY ./translation_cms-httpd.conf /etc/apache2/sites-available/translation_cms-httpd.conf
COPY ./website/translation_cms.wsgi /var/www/translation_cms/
COPY ./website/run.py /var/www/translation_cms/
COPY ./website/app /var/www/translation_cms/app

# Flag is stored in database via environment variable, not in filesystem
ARG FLAG="PLACEHOLDER_FLAG"
ENV FLAG=$FLAG

RUN chown -R www-data:www-data /var/www/translation_cms/
RUN chmod -R 755 /var/www/translation_cms/

RUN a2dissite 000-default.conf
RUN a2ensite translation_cms-httpd.conf
RUN a2enmod headers

CMD  /usr/sbin/apache2ctl -D FOREGROUND
