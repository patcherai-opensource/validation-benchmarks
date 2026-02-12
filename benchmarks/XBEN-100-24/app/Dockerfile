FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG=FLAG_PLACEHOLDER
ENV FLAG=${FLAG}

EXPOSE 5013

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=5 \
  CMD curl -f http://localhost:5013/ || exit 1

CMD ["python", "app.py"]
