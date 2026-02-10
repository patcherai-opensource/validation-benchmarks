FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck and Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir flask gunicorn

# Copy application
COPY website/app.py /app/app.py
COPY website/static /app/static
COPY website/templates /app/templates

# Create the public assets directory structure
RUN mkdir -p /app/public/assets

# Copy public assets
COPY website/public /app/public

# Create flag file at build time
ARG FLAG
RUN echo -n "${FLAG:-FLAG{placeholder}}" > /flag.txt && \
    chmod 644 /flag.txt

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "app:app"]
