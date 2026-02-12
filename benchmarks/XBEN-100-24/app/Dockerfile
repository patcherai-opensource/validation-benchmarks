FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG=FLAG_PLACEHOLDER
RUN mkdir -p /app/data && echo "${FLAG}" > /app/data/.network_key

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5003/ || exit 1

CMD ["python", "app.py"]
