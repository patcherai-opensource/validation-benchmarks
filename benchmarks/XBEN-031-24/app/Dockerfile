FROM python:3.11-slim

WORKDIR /app

# Install dependencies first
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install flask gunicorn

COPY app.py /app/app.py
COPY templates /app/templates

ARG FLAG
ENV FLAG=${FLAG}

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
