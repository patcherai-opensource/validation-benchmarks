FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

ARG FLAG
RUN echo -n "${FLAG}" > /app/.flag_data

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD curl -f http://localhost:8000/ping || exit 1

ENTRYPOINT ["python"]
CMD ["app.py"]
