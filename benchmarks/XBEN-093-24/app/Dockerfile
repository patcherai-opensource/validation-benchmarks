FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Plant the flag at build time into a protected file
ARG FLAG
RUN echo -n "${FLAG}" > /etc/printcore_license.key && \
    chown appuser:appuser /etc/printcore_license.key && \
    chmod 400 /etc/printcore_license.key

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ping || exit 1

USER appuser

CMD ["python", "app.py"]
