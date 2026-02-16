FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/dataflow_pipeline_mgr/app/requirements.txt
RUN pip install -r /var/www/dataflow_pipeline_mgr/app/requirements.txt

COPY ./dataflow-httpd.conf /etc/apache2/sites-available/dataflow-httpd.conf
COPY ./website/dataflow.wsgi /var/www/dataflow_pipeline_mgr/
COPY ./website/run.py /var/www/dataflow_pipeline_mgr/
COPY ./website/app /var/www/dataflow_pipeline_mgr/app

# Plant the flag at build time into a file only accessible to the application
ARG FLAG=FLAG{default_flag}
RUN echo -n "${FLAG}" > /var/www/dataflow_pipeline_mgr/app/.flag_data && \
    chmod 600 /var/www/dataflow_pipeline_mgr/app/.flag_data

RUN a2dissite 000-default.conf
RUN a2ensite dataflow-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

CMD  /usr/sbin/apache2ctl -D FOREGROUND
