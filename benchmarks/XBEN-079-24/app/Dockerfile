FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY website /app/

ARG FLAG
RUN echo -n "${FLAG}" > /var/secrets/flag.txt 2>/dev/null || \
    (mkdir -p /var/secrets && echo -n "${FLAG}" > /var/secrets/flag.txt)

RUN chmod 644 /var/secrets/flag.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 80

CMD ["python", "app.py"]
