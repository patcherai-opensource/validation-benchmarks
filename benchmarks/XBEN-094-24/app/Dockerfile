FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Remove any stale data
RUN rm -f flag.txt instance/urls.db instance/trytond.db

ARG FLAG
RUN echo -n "${FLAG}" > /var/lib/trytond_secret.txt && \
    chmod 600 /var/lib/trytond_secret.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/login || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
