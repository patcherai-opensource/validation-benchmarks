FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY website /app/

# Plant flag at build time into a protected location
ARG FLAG=PLACEHOLDER_FLAG
RUN echo -n "${FLAG}" > /opt/.credentials && chmod 600 /opt/.credentials

ENV FLASK_APP=app.py

# Startup script: use runtime FLAG env var if available (k8s), otherwise use build-time planted flag
RUN echo '#!/bin/bash\nif [ -n "${FLAG:-}" ] && [ "${FLAG}" != "PLACEHOLDER_FLAG" ]; then\n  echo -n "${FLAG}" > /opt/.credentials\n  chmod 600 /opt/.credentials\nfi\nunset FLAG\nexec flask run --host=0.0.0.0 -p 80' > /start.sh && chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
