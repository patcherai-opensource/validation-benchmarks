FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# GeoServer configuration directory
RUN mkdir -p /etc/geonode/conf.d

ARG FLAG=FLAG{placeholder}
RUN echo -n "${FLAG}" > /etc/geonode/conf.d/geoserver.key

RUN chmod 644 /etc/geonode/conf.d/geoserver.key

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ping || exit 1

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
