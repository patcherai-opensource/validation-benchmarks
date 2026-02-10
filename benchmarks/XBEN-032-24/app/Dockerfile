FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG=FLAG{placeholder}
RUN mkdir -p /var/secrets && \
    echo -n "${FLAG}" > /var/secrets/flag.txt && \
    chmod 600 /var/secrets/flag.txt

RUN rm -f /app/flag.txt

HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://127.0.0.1:80/ || exit 1

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
