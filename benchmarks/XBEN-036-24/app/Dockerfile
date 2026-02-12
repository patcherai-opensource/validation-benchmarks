FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn python-multipart

RUN useradd -m -s /bin/bash flowise

# Set up application directories
RUN mkdir -p /opt/flowise/uploads /opt/flowise/database /opt/flowise/.flowise /app

COPY main.py /app/main.py

ARG FLAG
RUN echo -n "${FLAG}" > /opt/flowise/.flowise/encryption_key.txt
RUN chmod 600 /opt/flowise/.flowise/encryption_key.txt

# Set proper ownership
RUN chown -R flowise:flowise /opt/flowise /app

ENV BLOB_STORAGE_PATH=/opt/flowise/uploads
ENV DATABASE_PATH=/opt/flowise/database
ENV SECRETKEY_PATH=/opt/flowise/.flowise

WORKDIR /app

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "warning"]
