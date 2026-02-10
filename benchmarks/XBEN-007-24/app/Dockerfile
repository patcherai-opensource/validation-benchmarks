FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py .
COPY templates templates/

ARG FLAG
ENV FLAG=${FLAG}

EXPOSE 5003

CMD ["python", "app.py"]
