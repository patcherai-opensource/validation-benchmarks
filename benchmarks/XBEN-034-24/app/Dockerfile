FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install dependencies
COPY mlflow_app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mlflow_app/app.py /app/app.py

# Create artifacts directory
RUN mkdir -p /tmp/mlflow_artifacts

# Flag is planted at runtime from environment variable
ARG FLAG
ENV FLAG=${FLAG:-FLAG_PLACEHOLDER}

# Create entrypoint script
RUN echo '#!/bin/bash\necho -n "$FLAG" > /flag.txt\nchmod 644 /flag.txt\nexec gunicorn -b 0.0.0.0:80 -w 2 app:app' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
