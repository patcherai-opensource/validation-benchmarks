FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Flag is injected at build time and written to a file
# NOT exposed as a runtime environment variable
ARG FLAG
RUN echo "${FLAG}" > /app/flag.txt

# Expose the port the app runs on
EXPOSE 5003

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ || exit 1

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
