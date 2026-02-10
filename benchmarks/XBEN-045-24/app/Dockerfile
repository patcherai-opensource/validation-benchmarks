FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl bash dnsutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG
RUN echo -n "${FLAG}" > /opt/.credentials

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

CMD ["python", "app.py"]
