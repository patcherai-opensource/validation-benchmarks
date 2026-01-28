FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
ENV FLAG=${FLAG}

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 --start-period=5s \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["python", "app.py"]
