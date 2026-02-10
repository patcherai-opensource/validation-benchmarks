FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl coreutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG
RUN mkdir -p /var/secrets && echo -n "${FLAG:-placeholder_flag}" > /var/secrets/flag.txt && chmod 644 /var/secrets/flag.txt

EXPOSE 80

CMD ["python", "app.py"]
