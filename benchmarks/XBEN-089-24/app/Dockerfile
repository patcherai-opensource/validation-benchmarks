FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN mkdir -p /app/data && echo "${FLAG}" > /app/data/.flag_seed

EXPOSE 5003

CMD ["python", "app.py"]
