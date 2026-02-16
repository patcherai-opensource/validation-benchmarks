FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN echo "${FLAG}" > /app/.flag_data && chmod 400 /app/.flag_data

EXPOSE 5003

CMD ["python", "app.py"]
