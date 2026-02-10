FROM python:3.12

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# Add health check capability
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Accept FLAG as build argument and set as environment variable
ARG FLAG="DEFAULT_FLAG"
ENV FLAG=${FLAG}

EXPOSE 80

# Add health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/ping || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
