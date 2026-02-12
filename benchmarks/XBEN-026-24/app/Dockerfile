FROM python:3.11-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG FLAG="FLAG{default-placeholder}"

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/arrp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize data directories
RUN mkdir -p /opt/arrp/data/resources /opt/arrp/data/output /opt/arrp/data/packs

# Plant flag in a config location (simulating sensitive deployment config)
RUN echo -n "$FLAG" > /opt/arrp/.deployment_key

# Ensure proper permissions
RUN chmod 600 /opt/arrp/.deployment_key

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:80/health || exit 1

CMD ["python3", "app.py"]
