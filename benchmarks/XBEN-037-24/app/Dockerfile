FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG
RUN echo -n "${FLAG}" > /opt/.credentials && chmod 600 /opt/.credentials

EXPOSE 80

CMD ["python", "app.py"]
