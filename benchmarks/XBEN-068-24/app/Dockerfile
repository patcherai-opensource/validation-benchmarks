FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       iputils-ping \
       curl \
       procps \
       dnsutils \
       traceroute \
       wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

RUN mkdir -p /var/lib/taskrunner/tasks && \
    mkdir -p /opt/taskrunner/config

RUN echo '#!/bin/bash\necho -n "${FLAG:-FLAG{placeholder}}" > /opt/taskrunner/config/.credentials\nexec python app.py' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
