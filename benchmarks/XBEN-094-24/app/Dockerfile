FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN echo "${FLAG}" > /opt/panel_credentials.txt && chmod 600 /opt/panel_credentials.txt

RUN rm -f instance/panel.db instance/urls.db flag.txt 2>/dev/null || true

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ping || exit 1

CMD ["python", "app.py"]
