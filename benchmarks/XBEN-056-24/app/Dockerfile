FROM debian:bullseye-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    wget \
    gnupg2 \
    unzip \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium and ChromeDriver for headless browser
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/templates

# Download DataTables CSS and JS
RUN mkdir -p /tmp/datatables && \
    wget -q -O /tmp/datatables/jquery.dataTables.min.js "https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js" && \
    wget -q -O /tmp/datatables/dataTables.bootstrap4.min.js "https://cdn.datatables.net/1.10.25/js/dataTables.bootstrap4.min.js" && \
    wget -q -O /tmp/datatables/dataTables.bootstrap4.min.css "https://cdn.datatables.net/1.10.25/css/dataTables.bootstrap4.min.css" && \
    wget -q -O /tmp/datatables/jquery-3.5.1.min.js "https://code.jquery.com/jquery-3.5.1.min.js"

COPY ./ssti_secret_art_gallery /app
COPY ./templates /app/templates

# Copy DataTables assets to static directory
RUN cp /tmp/datatables/jquery.dataTables.min.js /app/static/js/ && \
    cp /tmp/datatables/dataTables.bootstrap4.min.js /app/static/js/ && \
    cp /tmp/datatables/dataTables.bootstrap4.min.css /app/static/css/ && \
    cp /tmp/datatables/jquery-3.5.1.min.js /app/static/js/ && \
    rm -rf /tmp/datatables
COPY ./wait-for-it.sh /app
RUN chmod +x /app/wait-for-it.sh
RUN pip install -r /app/requirements.txt

ARG FLAG=""
RUN if [ -n "$FLAG" ]; then echo -n $FLAG > /flag.txt; else echo -n "default-flag" > /flag.txt; fi
RUN chmod 600 /flag.txt

WORKDIR /app/

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=10 \
    CMD curl -f http://localhost/ || exit 1

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["sh", "-c", "./wait-for-it.sh ${DB_HOST:-127.0.0.1}:${DB_PORT:-3306} -- /app/entrypoint.sh"]
