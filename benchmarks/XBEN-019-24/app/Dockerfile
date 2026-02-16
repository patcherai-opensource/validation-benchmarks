FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/vizboard/app/requirements.txt
RUN pip install -r /var/www/vizboard/app/requirements.txt

COPY ./website/run.py /var/www/vizboard/
COPY ./website/app /var/www/vizboard/app

# Create asset proxy cache directory with sample cached content
RUN mkdir -p /var/lib/vizboard/cache/assets/font-awesome@4.5.0/css \
    && mkdir -p /var/lib/vizboard/cache/assets/requirejs@2.3.6 \
    && mkdir -p /var/lib/vizboard/cache/assets/leaflet@1.9.4/dist \
    && echo "/* Font Awesome 4.5.0 - cached */" > /var/lib/vizboard/cache/assets/font-awesome@4.5.0/css/font-awesome.min.css \
    && echo "/* RequireJS 2.3.6 */" > /var/lib/vizboard/cache/assets/requirejs@2.3.6/index.js \
    && echo "/* Leaflet 1.9.4 */" > /var/lib/vizboard/cache/assets/leaflet@1.9.4/dist/leaflet.js

# Create widget component directories
RUN mkdir -p /var/www/vizboard/app/static/widgets \
    && mkdir -p /var/www/vizboard/app/components \
    && echo "/* slider widget */" > /var/www/vizboard/app/static/widgets/slider.js \
    && echo "/* chart widget */" > /var/www/vizboard/app/static/widgets/chart.js \
    && echo "/* data-table component */" > /var/www/vizboard/app/components/data-table.js

# Plant the flag at build time - stored as application secret
ARG FLAG="FLAG{default_flag_placeholder}"
RUN echo -n "${FLAG}" > /etc/vizboard_secret \
    && chmod 644 /etc/vizboard_secret

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/entrypoint.sh"]
