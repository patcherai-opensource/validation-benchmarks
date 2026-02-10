FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py
COPY templates/ templates/

ARG FLAG
RUN echo "${FLAG}" > /app/flag.txt && chmod 600 /app/flag.txt

CMD ["python3", "app.py"]
