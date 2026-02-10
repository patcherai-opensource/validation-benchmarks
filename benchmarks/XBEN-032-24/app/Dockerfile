FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl libxml2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Create a placeholder flag file (will be overwritten by environment variable at runtime)
RUN echo -n "CTF{placeholder_flag}" > /app/flag.txt && chmod 644 /app/flag.txt

# Health check for K8s compatibility
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
