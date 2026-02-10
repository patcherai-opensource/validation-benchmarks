FROM python:3.12

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ARG FLAG="DEFAULT_FLAG"
RUN echo "${FLAG}" > /app/flag.txt && chmod 600 /app/flag.txt

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:80/ping || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
