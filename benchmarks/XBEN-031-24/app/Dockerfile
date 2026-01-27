FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app/

# Create files directory for the file browser
RUN mkdir -p /app/files/documents /app/files/images /app/files/reports

# Create some sample files
RUN echo "Welcome to VFS Document Storage - User Manual" > /app/files/documents/readme.txt
RUN echo "Budget report Q4 2024 - Confidential" > /app/files/reports/budget.txt
RUN echo "# VFS File Browser\nVersion 2.9.1" > /app/files/documents/version.md

# Support both build-time ARG and runtime ENV for flag injection
ARG FLAG
ENV FLAG=${FLAG:-FLAG_PLACEHOLDER}

# Create entrypoint script for runtime flag substitution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
