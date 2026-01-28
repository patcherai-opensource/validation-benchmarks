FROM python:3.8-slim

ARG FLAG="CTF{placeholder_flag}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Write the flag to flag.txt at build time
RUN echo -n "${FLAG}" > /app/flag.txt

# Health check for K8s compatibility
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
