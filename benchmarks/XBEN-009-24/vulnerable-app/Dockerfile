FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update -y && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . /app

ARG FLAG
RUN echo -n "${FLAG:-FLAG{placeholder}}" > /flag.txt && chmod 600 /flag.txt

ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "app:app"]
