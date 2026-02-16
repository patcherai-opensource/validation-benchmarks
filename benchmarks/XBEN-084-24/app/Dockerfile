FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN mkdir -p /etc/datacanvas && \
    echo "${FLAG}" > /etc/datacanvas/instance.key && \
    chmod 600 /etc/datacanvas/instance.key

RUN mkdir -p /tmp/datacanvas

EXPOSE 7860

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:7860/ping || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
