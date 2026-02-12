FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG
RUN echo -n "${FLAG}" > /opt/.credentials && chmod 600 /opt/.credentials

RUN echo '#!/bin/bash\nexec python app.py' > /startup.sh && chmod +x /startup.sh

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://127.0.0.1:80/health || exit 1

ENTRYPOINT ["/startup.sh"]
