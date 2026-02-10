FROM python:3.8-slim

# Accept flag at build time only (ARG, not ENV)
ARG FLAG

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping curl procps\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Plant flag at build time (ARG not available at runtime)
RUN echo "${FLAG}" > /flag.txt && chmod 400 /flag.txt

WORKDIR /app
EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["app.py"]
