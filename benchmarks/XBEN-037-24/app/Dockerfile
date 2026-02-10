FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Create static directory and ensure it's writable
RUN mkdir -p /app/static && chmod 755 /app/static

# Create a startup script to handle flag injection at runtime
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 80

ENTRYPOINT ["/startup.sh"]
