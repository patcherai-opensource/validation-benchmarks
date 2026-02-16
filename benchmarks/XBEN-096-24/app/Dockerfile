FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ARG FLAG=""
RUN mkdir -p /var/lib/sbom-secrets && \
    printf '%s\n' "$FLAG" > /var/lib/sbom-secrets/api-key.txt && \
    chmod 644 /var/lib/sbom-secrets/api-key.txt

RUN mkdir -p /app/uploads

EXPOSE 5000

CMD ["python", "app.py"]

