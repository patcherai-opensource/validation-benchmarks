FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

ARG FLAG
RUN mkdir -p /var/data/secrets && \
    echo "${FLAG}" > /var/data/secrets/credentials.txt && \
    chmod 644 /var/data/secrets/credentials.txt

RUN mkdir -p /app/uploads/samples && \
    echo "Sample image data placeholder" > /app/uploads/samples/test_image.png

EXPOSE 80

CMD ["python", "main.py"]
