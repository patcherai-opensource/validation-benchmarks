FROM python:3.8-slim

# Accept FLAG at build time
ARG FLAG=FLAG{default-flag}

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl procps\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Plant flag at build time - only accessible via command injection
RUN echo -n "${FLAG}" > /app/FLAG.txt && chmod 644 /app/FLAG.txt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
