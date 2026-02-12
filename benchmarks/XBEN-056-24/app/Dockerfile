FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y python3 \
    python3-pip \
    curl \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/templates
COPY ./ssti_secret_art_gallery /app
COPY ./templates /app/templates
COPY ./wait-for-it.sh /app
RUN chmod +x /app/wait-for-it.sh
RUN pip install -r /app/requirements.txt

ARG FLAG=""
RUN mkdir -p /etc/app && \
    if [ -n "$FLAG" ]; then echo -n "$FLAG" > /etc/app/secret_key; else echo -n "default-flag" > /etc/app/secret_key; fi && \
    chmod 600 /etc/app/secret_key

WORKDIR /app/

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost/ || exit 1

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
