FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG=flag{placeholder}
RUN FLAG="${FLAG}" python init_database.py

EXPOSE 5003

CMD ["python", "app.py"]
