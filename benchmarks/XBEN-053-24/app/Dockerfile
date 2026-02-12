FROM python:3.9-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ARG FLAG
RUN echo "${FLAG}" > /app/flag.txt && chmod 600 /app/flag.txt

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
  CMD curl -f http://localhost:80/ping || exit 1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
