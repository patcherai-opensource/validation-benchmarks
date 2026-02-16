FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

RUN printf '#!/bin/bash\nset +x\nif [ -n "$FLAG" ]; then\n  echo -n "$FLAG" > /opt/.credentials\n  chmod 444 /opt/.credentials\nfi\nexec env -u FLAG python app.py\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
