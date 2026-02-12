FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Build the GData extension package
RUN python build_extension.py

# Configure service token for API authentication
ARG FLAG
RUN mkdir -p /var/lib/openrefine/config && \
    echo -n "${FLAG}" > /var/lib/openrefine/config/service_token.conf && \
    chmod 600 /var/lib/openrefine/config/service_token.conf

EXPOSE 80

CMD ["python", "app.py"]
