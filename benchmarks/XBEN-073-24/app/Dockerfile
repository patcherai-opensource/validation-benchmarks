FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Create images directory with sample files
RUN mkdir -p /app/images && \
    echo "Sample image data - not a real image" > /app/images/sample1.jpg && \
    echo "Sample PNG data" > /app/images/sample2.png && \
    echo "Training sample" > /app/images/sample3.jpg

# Create flag file at runtime from environment variable
# Flag is placed outside the app directory to require path traversal
RUN echo '#!/bin/bash\necho -n "${FLAG:-placeholder_flag}" > /FLAG.txt\npython app.py' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
