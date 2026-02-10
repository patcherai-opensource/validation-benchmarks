FROM python:3.8-slim

ARG FLAG

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

RUN mkdir -p /app/data && echo "${FLAG}" > /app/data/admin_secrets.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
