FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl clamav clamav-daemon \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

RUN mkdir -p /app/config /tmp/uploads /app/static && \
    chmod 755 /app/config /tmp/uploads /app/static

COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 80

ENTRYPOINT ["/startup.sh"]
