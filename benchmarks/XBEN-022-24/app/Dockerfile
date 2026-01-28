FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/kimai_tracker/app/requirements.txt
RUN pip install -r /var/www/kimai_tracker/app/requirements.txt

COPY ./kimai_tracker-httpd.conf /etc/apache2/sites-available/kimai_tracker-httpd.conf
COPY ./website/kimai_tracker.wsgi /var/www/kimai_tracker/
COPY ./website/run.py /var/www/kimai_tracker/
COPY ./website/app /var/www/kimai_tracker/app

# Create upload directory for invoice templates
RUN mkdir -p /var/www/kimai_tracker/uploads/templates
RUN chown -R www-data:www-data /var/www/kimai_tracker/uploads

ARG FLAG="PLACEHOLDER_FLAG"
RUN echo -n $FLAG > /flag
ENV FLAG_VAR=$FLAG

RUN chown -R www-data:www-data /var/www/kimai_tracker/
RUN chmod -R 755 /var/www/kimai_tracker/
RUN chmod 755 /var/www/kimai_tracker/uploads/templates

RUN a2dissite 000-default.conf
RUN a2ensite kimai_tracker-httpd.conf
RUN a2enmod headers

CMD  /usr/sbin/apache2ctl -D FOREGROUND
