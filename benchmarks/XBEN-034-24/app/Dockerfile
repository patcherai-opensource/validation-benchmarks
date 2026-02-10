FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY entrypoint.sh .

# Create tmp directory for artifact location
RUN mkdir -p /tmp/artifacts && \
    chmod 755 /tmp/artifacts

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 80

# Run the application via entrypoint
CMD ["/app/entrypoint.sh"]
