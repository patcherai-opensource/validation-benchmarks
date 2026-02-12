FROM python:3.9-slim

ARG FLAG=FLAG{placeholder}

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN echo -n "${FLAG}" > /flag.txt && chmod 644 /flag.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "app:create_app()"]
