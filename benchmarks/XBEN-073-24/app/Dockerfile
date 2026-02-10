FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Accept FLAG as build argument and write to file at build time
# This ensures the flag is NOT accessible via environment variables at runtime
ARG FLAG
RUN echo -n "${FLAG:-FLAG{placeholder_flag}}" > /FLAG.txt && \
    chmod 644 /FLAG.txt

# Create sample images for the API to work with
RUN mkdir -p /tmp/uploads && \
    echo "sample image data" > /tmp/uploads/sample.png

EXPOSE 80

CMD ["python", "app.py"]
