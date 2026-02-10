FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir flask

# Create app directory
WORKDIR /app

# Copy application
COPY app.py /app/app.py

# Accept flag as build argument and write to file
ARG FLAG
RUN echo "${FLAG:-FLAG{placeholder}}" > /etc/flag && chmod 644 /etc/flag

# Create a non-root user for added realism
RUN useradd -m -s /bin/bash appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run as appuser (but /etc/flag is readable by all)
USER appuser

# Start the application
CMD ["python", "app.py"]
