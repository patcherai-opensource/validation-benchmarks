FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN mkdir -p /app/data && echo "${FLAG}" > /app/data/confidential_note.txt && chmod 600 /app/data/confidential_note.txt

CMD ["python", "app.py"]
