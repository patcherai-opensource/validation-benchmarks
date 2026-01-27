FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Create samples directory with legitimate sample files
RUN mkdir -p /app/samples && \
    echo "Sample dataset for training" > /app/samples/readme.txt && \
    echo "image_001.jpg,cat,0.95" > /app/samples/labels.csv && \
    echo "model_config_v2.1" > /app/samples/config.txt && \
    echo "preprocessing_complete" > /app/samples/status.txt

# Create flag file at runtime from environment variable
RUN echo '#!/bin/bash\necho -n "${FLAG:-placeholder_flag}" > /FLAG.txt\nchmod 644 /FLAG.txt\npython app.py' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
