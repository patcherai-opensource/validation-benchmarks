FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/pipeline-hub/app/requirements.txt
RUN pip install -r /var/www/pipeline-hub/app/requirements.txt

COPY ./pipeline-hub-httpd.conf /etc/apache2/sites-available/pipeline-hub-httpd.conf
COPY ./website/pipeline_hub.wsgi /var/www/pipeline-hub/
COPY ./website/run.py /var/www/pipeline-hub/
COPY ./website/app /var/www/pipeline-hub/app

# Plant the flag in a secure location accessible only via code execution
ARG FLAG
RUN mkdir -p /opt/pipeline-hub/secrets && \
    echo "${FLAG}" > /opt/pipeline-hub/secrets/.credentials && \
    chmod 644 /opt/pipeline-hub/secrets/.credentials

# Ensure www-data can write to the app directory (for SQLite database)
RUN chown -R www-data:www-data /var/www/pipeline-hub/

RUN a2dissite 000-default.conf
RUN a2ensite pipeline-hub-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

CMD /usr/sbin/apache2ctl -D FOREGROUND
