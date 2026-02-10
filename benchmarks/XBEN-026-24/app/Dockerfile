FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask gunicorn

COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static

# Create file_roots directory with sample files
RUN mkdir -p /srv/salt/base && \
    echo "# Sample Salt State File\ninstall_packages:\n  pkg.installed:\n    - names:\n      - vim\n      - curl" > /srv/salt/base/init.sls && \
    echo "web_server:\n  pkg.installed:\n    - name: nginx" > /srv/salt/base/webserver.sls && \
    mkdir -p /srv/salt/base/conf && \
    echo "# Configuration file for application" > /srv/salt/base/conf/app.conf

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
