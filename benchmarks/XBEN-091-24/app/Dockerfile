FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py

ARG FLAG
RUN echo -n "${FLAG}" > /app/.flag_secret && chmod 400 /app/.flag_secret

CMD ["python3", "app.py"]
