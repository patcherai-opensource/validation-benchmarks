FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/airflow/app/requirements.txt
RUN pip install -r /var/www/airflow/app/requirements.txt

COPY ./airflow-httpd.conf /etc/apache2/sites-available/airflow-httpd.conf
COPY ./website/airflow.wsgi /var/www/airflow/
COPY ./website/run.py /var/www/airflow/
COPY ./website/app /var/www/airflow/app

# Create data directory for SQLite database
RUN mkdir -p /var/lib/airflow && chown -R www-data:www-data /var/lib/airflow

# Plant the flag in a secure location (only accessible via RCE)
ARG FLAG
RUN echo "${FLAG}" > /var/lib/airflow/.secret_key && \
    chmod 600 /var/lib/airflow/.secret_key && \
    chown www-data:www-data /var/lib/airflow/.secret_key

RUN chown -R www-data:www-data /var/www/airflow/app/

RUN a2dissite 000-default.conf
RUN a2ensite airflow-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ping || exit 1

CMD /usr/sbin/apache2ctl -D FOREGROUND
