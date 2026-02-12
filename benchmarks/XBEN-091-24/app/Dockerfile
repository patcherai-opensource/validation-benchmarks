FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py
COPY templates/ templates/
COPY config/ config/

ARG FLAG
ENV FLAG=$FLAG

CMD ["python3", "app.py"]
