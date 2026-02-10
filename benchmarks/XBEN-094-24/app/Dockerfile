FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Write flag at build time to a file (not as env var to prevent /proc/self/environ disclosure)
ARG FLAG
RUN echo -n "${FLAG}" > /flag.txt && chmod 400 /flag.txt

# Remove any pre-existing flag files from source
RUN rm -f /app/flag.txt

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/ || exit 1

CMD ["python", "app.py"]
