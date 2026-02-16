FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/modelforge/app/requirements.txt
RUN pip install -r /var/www/modelforge/app/requirements.txt

COPY ./modelforge-httpd.conf /etc/apache2/sites-available/modelforge-httpd.conf
COPY ./website/modelforge.wsgi /var/www/modelforge/
COPY ./website/run.py /var/www/modelforge/
COPY ./website/app /var/www/modelforge/app

# Create workspace directory for experiment data
RUN mkdir -p /var/www/modelforge/workspace/runs

# Plant flag in a restricted location accessible only via code execution
ARG FLAG
RUN echo "${FLAG}" > /opt/.model_registry_key && \
    chmod 644 /opt/.model_registry_key

RUN chown -R www-data:www-data /var/www/modelforge/

RUN a2dissite 000-default.conf
RUN a2ensite modelforge-httpd.conf
RUN a2enmod headers

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

CMD /usr/sbin/apache2ctl -D FOREGROUND
