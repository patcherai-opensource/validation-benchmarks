FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG FLAG
RUN mkdir -p /data && \
    APP_INIT_TOKEN="${FLAG}" python -c "from app.create_app import create_app; create_app()" && \
    unset APP_INIT_TOKEN

ENV JWT_SECRET_KEY="a7f3c8d1e9b24f5a8c6d0e2f4a7b9c1d"

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "wsgi:application"]
