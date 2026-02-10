FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Accept FLAG as build argument and write to file (not env var)
ARG FLAG
RUN mkdir -p /app/secret && \
    echo "${FLAG}" > /app/secret/flag.txt && \
    chmod 600 /app/secret/flag.txt

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ || exit 1

CMD ["python", "app.py"]
