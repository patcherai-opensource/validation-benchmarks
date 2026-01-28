FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Support both build-time ARG and runtime ENV for FLAG
ARG FLAG
ENV FLAG=${FLAG}

EXPOSE 80

CMD ["python", "/app/app.py"]
