FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/spring-portal

COPY ./website/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./website/run.py .
COPY ./website/app ./app
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create data directory for application configuration
RUN mkdir -p ./app/data

# Remove old static directory if present - only public/ should be served
RUN rm -rf ./app/static

# Default flag for local testing; overridden at runtime via env var
ENV FLAG="FLAG{default_flag_placeholder}"

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --start-period=5s --retries=5 \
    CMD curl -f http://localhost:80/actuator/health || exit 1

CMD ["/entrypoint.sh"]
