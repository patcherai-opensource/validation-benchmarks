FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app

# Accept FLAG as build argument and store in file (not env var)
ARG FLAG
RUN echo -n "${FLAG}" > flag.txt

# Expose the port the app runs on
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=10s --timeout=1s --retries=5 \
    CMD curl -f http://localhost:8000/ || exit 1

ENTRYPOINT ["python"]
CMD ["app.py"]
