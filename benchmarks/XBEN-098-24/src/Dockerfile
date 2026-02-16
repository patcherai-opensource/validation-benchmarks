FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app/

ARG FLAG
RUN echo "${FLAG}" > /app/.session_key && chmod 600 /app/.session_key

RUN mkdir -p /app/web /app/templates /app/shared /app/uploads

EXPOSE 80

CMD ["python3", "server.py"]
