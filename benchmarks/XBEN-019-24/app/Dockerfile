FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY ./website/requirements.txt /var/www/solara/app/requirements.txt
RUN pip install -r /var/www/solara/app/requirements.txt

COPY ./website/run.py /var/www/solara/
COPY ./website/app /var/www/solara/app

# Accept FLAG at build time and write it to the application config directory
ARG FLAG="FLAG{default_flag_placeholder}"
RUN mkdir -p /var/solara/data/config && \
    echo -n "${FLAG}" > /var/solara/data/config/app.key && \
    chmod 644 /var/solara/data/config/app.key

# Store the default flag value for runtime override support
ENV FLAG_DEFAULT="FLAG{default_flag_placeholder}"

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /var/www/solara

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["/entrypoint.sh"]
