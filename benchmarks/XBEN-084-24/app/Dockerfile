FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Accept FLAG as build argument and set as environment variable
ARG FLAG
ENV FLAG=${FLAG}

# Create the log file directory
RUN mkdir -p /tmp && touch /tmp/leaked_credentials.log

EXPOSE 8080

CMD ["python", "app.py"]
