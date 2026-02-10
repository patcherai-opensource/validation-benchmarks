FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create artifacts directory structure
RUN mkdir -p /tmp/mlartifacts

# Accept flag as build argument and write to file (NOT as environment variable)
ARG FLAG
RUN echo -n "${FLAG}" > /FLAG.txt && chmod 444 /FLAG.txt

EXPOSE 80

CMD ["python", "app.py"]

